from __future__ import annotations

import argparse
import json
import math
import sys
from collections import Counter
from pathlib import Path

from common import DEFAULT_CHUNKS, load_chunk_records, resolve_chunks_path, tokenize

try:
    from src.finance_report_assistant.retrieval.embedding import HashEmbeddingIndex
except ModuleNotFoundError:
    REPO_ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from src.finance_report_assistant.retrieval.embedding import HashEmbeddingIndex


def _cosine_sparse(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    dot = sum(v * b.get(k, 0.0) for k, v in a.items())
    if dot == 0:
        return 0.0
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def _bow_vectors(texts: list[str]) -> list[dict[str, float]]:
    vectors: list[dict[str, float]] = []
    for text in texts:
        freq = Counter(tokenize(text))
        vectors.append({k: float(v) for k, v in freq.items()})
    return vectors


def _tfidf_vectors(texts: list[str]) -> list[dict[str, float]]:
    docs = [tokenize(t) for t in texts]
    n_docs = len(docs)
    df: Counter[str] = Counter()
    for doc in docs:
        df.update(set(doc))

    vectors: list[dict[str, float]] = []
    for doc in docs:
        tf = Counter(doc)
        vec: dict[str, float] = {}
        for tok, count in tf.items():
            idf = math.log((1 + n_docs) / (1 + df[tok])) + 1.0
            vec[tok] = float(count) * idf
        vectors.append(vec)
    return vectors


def _neighbor_overlap_score(vectors: list[dict[str, float]], labels: list[str], top_k: int = 5) -> float:
    """
    Proxy metric: for each chunk, measure whether nearest neighbors tend to share section prefix.
    """
    if not vectors:
        return 0.0

    hits = 0
    total = 0
    for i, vec_i in enumerate(vectors):
        scores: list[tuple[int, float]] = []
        for j, vec_j in enumerate(vectors):
            if i == j:
                continue
            scores.append((j, _cosine_sparse(vec_i, vec_j)))
        top = sorted(scores, key=lambda x: x[1], reverse=True)[:top_k]
        label_i = labels[i].split(".")[0].lower().strip()
        for j, _ in top:
            label_j = labels[j].split(".")[0].lower().strip()
            total += 1
            if label_i and label_i == label_j:
                hits += 1
    return hits / total if total else 0.0


def _hash_vectors(texts: list[str], dim: int) -> list[dict[str, float]]:
    index = HashEmbeddingIndex.fit(texts, dim=dim)
    vectors: list[dict[str, float]] = []
    for dv in index.doc_vectors:
        vectors.append({str(k): v for k, v in dv.items()})
    return vectors


def _describe_methods() -> list[dict[str, str]]:
    return [
        {
            "method": "bow",
            "idea": "Local count-based representation of each chunk.",
            "relation_to_word2vec_glove": "Baseline only (no learned dense semantics).",
        },
        {
            "method": "tfidf",
            "idea": "Downweights common terms, highlights informative terms.",
            "relation_to_word2vec_glove": "Still sparse; often strong lexical baseline.",
        },
        {
            "method": "hash_embedding",
            "idea": "Dense-ish hashed feature vector with character + bigram cues.",
            "relation_to_word2vec_glove": "Approximate semantic retrieval without external model weights.",
        },
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="Embedding playground: compare representation families")
    parser.add_argument("--chunks", type=Path, default=DEFAULT_CHUNKS)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--hash-dim", type=int, default=384)
    parser.add_argument("--output-md", type=Path, default=None)
    args = parser.parse_args()

    chunks_path = resolve_chunks_path(args.chunks)
    if not chunks_path.exists():
        raise SystemExit(f"Chunks file not found: {chunks_path}")

    records = load_chunk_records(chunks_path)
    if len(records) < 3:
        raise SystemExit("Need at least 3 chunks for embedding comparison")

    texts = [r["text"] for r in records]
    labels = [r.get("section_title", "") for r in records]

    bow_score = _neighbor_overlap_score(_bow_vectors(texts), labels, top_k=args.top_k)
    tfidf_score = _neighbor_overlap_score(_tfidf_vectors(texts), labels, top_k=args.top_k)
    hash_score = _neighbor_overlap_score(_hash_vectors(texts, dim=args.hash_dim), labels, top_k=args.top_k)

    rows = [
        {
            "method": "bow",
            "neighbor_label_overlap": round(bow_score, 4),
            "note": "Simple sparse baseline",
        },
        {
            "method": "tfidf",
            "neighbor_label_overlap": round(tfidf_score, 4),
            "note": "Sparse lexical weighting",
        },
        {
            "method": "hash_embedding",
            "neighbor_label_overlap": round(hash_score, 4),
            "note": "Dense-ish semantic proxy",
        },
    ]

    table = [
        "| Method | Neighbor Label Overlap@K | Notes |",
        "| --- | ---: | --- |",
    ]
    for row in rows:
        table.append(
            f"| {row['method']} | {row['neighbor_label_overlap']:.4f} | {row['note']} |"
        )

    payload = {
        "chunks": str(chunks_path),
        "doc_count": len(records),
        "top_k": args.top_k,
        "method_notes": _describe_methods(),
        "results": rows,
        "markdown_table": "\n".join(table),
    }
    print(json.dumps(payload, indent=2))

    if args.output_md is not None:
        out_path = args.output_md if args.output_md.is_absolute() else (Path.cwd() / args.output_md).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n".join(table) + "\n", encoding="utf-8")
        print(f"\nWrote markdown table: {out_path}")


if __name__ == "__main__":
    main()
