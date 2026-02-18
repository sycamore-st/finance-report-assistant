from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
import re

from finance_report_assistant.retrieval.hybrid import fuse_rankings
from finance_report_assistant.retrieval.index import RetrievalIndex

TOKEN_RE = re.compile(r"[a-z0-9]+")
QUERY_TYPES: dict[str, set[str]] = {
    "risk": {"risk", "uncertain", "litigation", "disruption", "exposure"},
    "growth": {"growth", "demand", "innovation", "market", "expand"},
    "liquidity": {"liquidity", "cash", "debt", "capital", "flow", "financing"},
    "guidance": {"guidance", "outlook", "expect", "forecast", "project", "target"},
}


@dataclass
class EvalQuery:
    query_id: str
    query: str
    target_chunk_id: str
    section_title: str
    query_type: str


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall((text or "").lower())


def _infer_query_type(text: str) -> str:
    terms = set(_tokenize(text))
    best_type = "general"
    best_hits = 0
    for qtype, keywords in QUERY_TYPES.items():
        hits = len(terms & keywords)
        if hits > best_hits:
            best_hits = hits
            best_type = qtype
    return best_type


def build_eval_queries(records: list[dict], max_queries: int = 30) -> list[EvalQuery]:
    out: list[EvalQuery] = []
    for idx, row in enumerate(records[:max_queries]):
        terms: list[str] = []
        for tok in _tokenize(row.get("text", "")):
            if len(tok) < 5:
                continue
            if tok in terms:
                continue
            terms.append(tok)
            if len(terms) >= 4:
                break

        section = (row.get("section_title") or "").strip()
        query_text = f"{section} {' '.join(terms)}".strip()
        if not query_text:
            continue

        out.append(
            EvalQuery(
                query_id=f"q{idx + 1}",
                query=query_text,
                target_chunk_id=str(row.get("chunk_id", "")),
                section_title=section or "Unknown",
                query_type=_infer_query_type(query_text),
            )
        )
    return out


def _rank_bm25(index: RetrievalIndex, query: str, top_k: int) -> list[str]:
    scores = index.bm25.scores(query)
    ranked = sorted(range(len(index.records)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [str(index.records[i].get("chunk_id", "")) for i in ranked]


def _rank_embedding(index: RetrievalIndex, query: str, top_k: int) -> list[str]:
    scores = index.embedding.scores(query)
    ranked = sorted(range(len(index.records)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [str(index.records[i].get("chunk_id", "")) for i in ranked]


def _rank_hybrid(index: RetrievalIndex, query: str, top_k: int, bm25_weight: float) -> list[str]:
    emb_weight = 1.0 - bm25_weight
    bm25_scores = index.bm25.scores(query)
    emb_scores = index.embedding.scores(query)
    hits = fuse_rankings(
        records=index.records,
        bm25_scores=bm25_scores,
        embedding_scores=emb_scores,
        top_k=top_k,
        bm25_weight=bm25_weight,
        embedding_weight=emb_weight,
    )
    return [str(h.record.get("chunk_id", "")) for h in hits]


def _compute_metrics(queries: list[EvalQuery], ranked: dict[str, list[str]]) -> dict[str, float]:
    if not queries:
        return {"hit@k": 0.0, "mrr": 0.0}

    hit = 0
    rr = 0.0
    for q in queries:
        results = ranked.get(q.query_id, [])
        if q.target_chunk_id in results:
            hit += 1
            rr += 1.0 / (results.index(q.target_chunk_id) + 1)

    n = len(queries)
    return {"hit@k": hit / n, "mrr": rr / n}


def _slice_metrics(
    queries: list[EvalQuery],
    ranked: dict[str, list[str]],
    slice_key: str,
) -> dict[str, dict[str, float]]:
    bucketed: dict[str, list[EvalQuery]] = {}
    for q in queries:
        key = getattr(q, slice_key)
        bucketed.setdefault(key, []).append(q)

    out: dict[str, dict[str, float]] = {}
    for key, group in bucketed.items():
        out[key] = _compute_metrics(group, ranked)
    return out


def _misses(
    queries: list[EvalQuery],
    ranked: dict[str, list[str]],
    limit: int = 20,
) -> list[dict]:
    misses: list[dict] = []
    for q in queries:
        results = ranked.get(q.query_id, [])
        if q.target_chunk_id in results:
            continue
        misses.append(
            {
                "query_id": q.query_id,
                "query": q.query,
                "query_type": q.query_type,
                "section_title": q.section_title,
                "expected_chunk_id": q.target_chunk_id,
                "predicted_top_k": results,
            }
        )
        if len(misses) >= limit:
            break
    return misses


def _weight_sweep(index: RetrievalIndex, queries: list[EvalQuery], top_k: int) -> list[dict]:
    weights = [0.0, 0.25, 0.5, 0.55, 0.75, 1.0]
    rows: list[dict] = []
    for w in weights:
        ranked: dict[str, list[str]] = {}
        for q in queries:
            ranked[q.query_id] = _rank_hybrid(index, q.query, top_k=top_k, bm25_weight=w)
        metrics = _compute_metrics(queries, ranked)
        rows.append({"bm25_weight": w, "embedding_weight": 1.0 - w, **metrics})
    return rows


def evaluate_retrieval(
    index: RetrievalIndex,
    top_k: int = 5,
    max_queries: int = 30,
    error_limit: int = 20,
    bm25_weight: float = 0.55,
) -> dict:
    queries = build_eval_queries(index.records, max_queries=max_queries)
    if not queries:
        raise ValueError("No evaluation queries were generated")

    bm25_ranked: dict[str, list[str]] = {}
    embedding_ranked: dict[str, list[str]] = {}
    hybrid_ranked: dict[str, list[str]] = {}

    for q in queries:
        bm25_ranked[q.query_id] = _rank_bm25(index, q.query, top_k=top_k)
        embedding_ranked[q.query_id] = _rank_embedding(index, q.query, top_k=top_k)
        hybrid_ranked[q.query_id] = _rank_hybrid(index, q.query, top_k=top_k, bm25_weight=bm25_weight)

    rows = [
        {"retriever": "bm25", **_compute_metrics(queries, bm25_ranked)},
        {"retriever": "embedding", **_compute_metrics(queries, embedding_ranked)},
        {"retriever": "hybrid_rrf", **_compute_metrics(queries, hybrid_ranked)},
    ]

    sweep = _weight_sweep(index, queries, top_k=top_k)
    best = max(sweep, key=lambda x: (x["mrr"], x["hit@k"]))

    slices = {
        "by_section": _slice_metrics(queries, hybrid_ranked, slice_key="section_title"),
        "by_query_type": _slice_metrics(queries, hybrid_ranked, slice_key="query_type"),
    }

    errors = {
        "bm25": _misses(queries, bm25_ranked, limit=error_limit),
        "embedding": _misses(queries, embedding_ranked, limit=error_limit),
        "hybrid_rrf": _misses(queries, hybrid_ranked, limit=error_limit),
    }

    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "top_k": top_k,
        "query_count": len(queries),
        "results": rows,
        "weight_sweep": sweep,
        "best_weight": best,
        "slices": slices,
        "errors": errors,
        "sample_queries": [q.__dict__ for q in queries[:5]],
    }


def render_summary_markdown(payload: dict, ticker: str, form: str) -> str:
    lines = [
        f"\n## Retrieval Eval - {payload['timestamp']}",
        f"- Ticker/Form: `{ticker.upper()} {form}`",
        f"- Queries: {payload['query_count']}",
        f"- Top-K: {payload['top_k']}",
        "",
        "| Retriever | Hit@K | MRR |",
        "| --- | ---: | ---: |",
    ]
    for row in payload["results"]:
        lines.append(f"| {row['retriever']} | {row['hit@k']:.4f} | {row['mrr']:.4f} |")

    best = payload["best_weight"]
    lines.extend(
        [
            "",
            "### Hybrid Weight Sweep Best",
            f"- bm25_weight: {best['bm25_weight']}",
            f"- embedding_weight: {best['embedding_weight']}",
            f"- hit@k: {best['hit@k']:.4f}",
            f"- mrr: {best['mrr']:.4f}",
        ]
    )
    return "\n".join(lines) + "\n"


def render_error_analysis_markdown(payload: dict, ticker: str, form: str) -> str:
    lines = [
        f"# Retrieval Error Analysis ({ticker.upper()} {form})",
        f"\nGenerated: {payload['timestamp']}",
        f"\nTop-K: {payload['top_k']} | Queries: {payload['query_count']}",
        "\n## By Query Type (hybrid)",
        "| Query Type | Hit@K | MRR |",
        "| --- | ---: | ---: |",
    ]
    for qtype, metrics in sorted(payload["slices"]["by_query_type"].items()):
        lines.append(f"| {qtype} | {metrics['hit@k']:.4f} | {metrics['mrr']:.4f} |")

    lines.extend([
        "\n## By Section (hybrid)",
        "| Section | Hit@K | MRR |",
        "| --- | ---: | ---: |",
    ])
    for section, metrics in sorted(payload["slices"]["by_section"].items()):
        lines.append(f"| {section} | {metrics['hit@k']:.4f} | {metrics['mrr']:.4f} |")

    lines.append("\n## Failure Examples")
    for retriever, misses in payload["errors"].items():
        lines.append(f"\n### {retriever}")
        if not misses:
            lines.append("- No misses in sampled queries.")
            continue
        for m in misses[:10]:
            lines.append(
                f"- `{m['query_id']}` ({m['query_type']}) expected `{m['expected_chunk_id']}` got {m['predicted_top_k']}"
            )
            lines.append(f"  - Query: {m['query']}")

    return "\n".join(lines) + "\n"
