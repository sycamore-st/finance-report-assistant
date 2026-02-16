from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from common import (
    DEFAULT_CHUNKS,
    build_lightweight_eval_queries,
    load_chunk_records,
    resolve_chunks_path,
)

try:
    from src.finance_report_assistant.retrieval.bm25 import BM25Index
    from src.finance_report_assistant.retrieval.embedding import HashEmbeddingIndex
    from src.finance_report_assistant.retrieval.hybrid import fuse_rankings
except ModuleNotFoundError:
    REPO_ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from src.finance_report_assistant.retrieval.bm25 import BM25Index
    from src.finance_report_assistant.retrieval.embedding import HashEmbeddingIndex
    from src.finance_report_assistant.retrieval.hybrid import fuse_rankings


def _rank_bm25(records: list[dict], bm25: BM25Index, query: str, top_k: int) -> list[str]:
    scores = bm25.scores(query)
    ranked = sorted(range(len(records)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [records[i]["chunk_id"] for i in ranked]


def _rank_embedding(
    records: list[dict], embedding: HashEmbeddingIndex, query: str, top_k: int
) -> list[str]:
    scores = embedding.scores(query)
    ranked = sorted(range(len(records)), key=lambda i: scores[i], reverse=True)[:top_k]
    return [records[i]["chunk_id"] for i in ranked]


def _rank_hybrid(
    records: list[dict],
    bm25: BM25Index,
    embedding: HashEmbeddingIndex,
    query: str,
    top_k: int,
) -> list[str]:
    bm25_scores = bm25.scores(query)
    emb_scores = embedding.scores(query)
    hits = fuse_rankings(
        records=records,
        bm25_scores=bm25_scores,
        embedding_scores=emb_scores,
        top_k=top_k,
        bm25_weight=0.55,
        embedding_weight=0.45,
    )
    return [h.record["chunk_id"] for h in hits]


def _metrics(queries: list[dict], ranked_by_query: dict[str, list[str]]) -> dict[str, float]:
    if not queries:
        return {"hit@k": 0.0, "mrr": 0.0}

    hits = 0
    rr_sum = 0.0
    for q in queries:
        qid = q["query_id"]
        target = q["target_chunk_id"]
        ranked = ranked_by_query.get(qid, [])

        if target in ranked:
            hits += 1
            rank = ranked.index(target) + 1
            rr_sum += 1.0 / rank

    n = len(queries)
    return {"hit@k": hits / n, "mrr": rr_sum / n}


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare BM25 vs embedding vs hybrid retrieval")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--max-queries", type=int, default=30)
    parser.add_argument("--hash-dim", type=int, default=384)
    parser.add_argument("--output-md", type=Path, default=None)
    args = parser.parse_args()

    chunks_path = resolve_chunks_path(args.chunks)
    if not chunks_path.exists():
        raise SystemExit(f"Chunks file not found: {chunks_path}")

    records = load_chunk_records(chunks_path)
    if len(records) < 3:
        raise SystemExit("Need at least 3 chunks for retrieval comparison")

    queries = build_lightweight_eval_queries(records, max_queries=args.max_queries)
    if not queries:
        raise SystemExit("No evaluation queries were generated")

    texts = [r["text"] for r in records]
    bm25 = BM25Index.fit(texts)
    embedding = HashEmbeddingIndex.fit(texts, dim=args.hash_dim)

    bm25_ranked: dict[str, list[str]] = {}
    embedding_ranked: dict[str, list[str]] = {}
    hybrid_ranked: dict[str, list[str]] = {}

    for q in queries:
        qid = q["query_id"]
        query = q["query"]
        bm25_ranked[qid] = _rank_bm25(records, bm25, query, top_k=args.top_k)
        embedding_ranked[qid] = _rank_embedding(records, embedding, query, top_k=args.top_k)
        hybrid_ranked[qid] = _rank_hybrid(records, bm25, embedding, query, top_k=args.top_k)

    bm25_metrics = _metrics(queries, bm25_ranked)
    emb_metrics = _metrics(queries, embedding_ranked)
    hybrid_metrics = _metrics(queries, hybrid_ranked)

    rows = [
        {"retriever": "bm25", **bm25_metrics},
        {"retriever": "embedding", **emb_metrics},
        {"retriever": "hybrid_rrf", **hybrid_metrics},
    ]

    table_lines = [
        "| Retriever | Hit@K | MRR |",
        "| --- | ---: | ---: |",
    ]
    for row in rows:
        table_lines.append(
            f"| {row['retriever']} | {row['hit@k']:.4f} | {row['mrr']:.4f} |"
        )

    payload = {
        "chunks": str(chunks_path),
        "doc_count": len(records),
        "query_count": len(queries),
        "top_k": args.top_k,
        "results": rows,
        "sample_queries": queries[:5],
        "markdown_table": "\n".join(table_lines),
    }
    print(json.dumps(payload, indent=2))

    if args.output_md is not None:
        out_path = args.output_md if args.output_md.is_absolute() else (Path.cwd() / args.output_md).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(table_lines) + "\n", encoding="utf-8")
        print(f"\nWrote markdown table: {out_path}")


if __name__ == "__main__":
    main()

