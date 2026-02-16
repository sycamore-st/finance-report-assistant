from __future__ import annotations

from dataclasses import dataclass


@dataclass
class RetrievalHit:
    rank: int
    score: float
    bm25_score: float
    embedding_score: float
    record: dict


def _rank_positions(scores: list[float]) -> dict[int, int]:
    ranked = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
    return {doc_idx: rank for rank, doc_idx in enumerate(ranked, start=1)}


def fuse_rankings(
    records: list[dict],
    bm25_scores: list[float],
    embedding_scores: list[float],
    top_k: int = 5,
    bm25_weight: float = 0.55,
    embedding_weight: float = 0.45,
    rrf_k: int = 60,
) -> list[RetrievalHit]:
    if not records:
        return []

    bm25_ranks = _rank_positions(bm25_scores)
    emb_ranks = _rank_positions(embedding_scores)

    scored: list[tuple[int, float]] = []
    for i in range(len(records)):
        r_bm25 = bm25_ranks[i]
        r_emb = emb_ranks[i]
        score = bm25_weight / (rrf_k + r_bm25) + embedding_weight / (rrf_k + r_emb)
        scored.append((i, score))

    ranked = sorted(scored, key=lambda x: x[1], reverse=True)[:top_k]

    hits: list[RetrievalHit] = []
    for rank, (doc_idx, score) in enumerate(ranked, start=1):
        hits.append(
            RetrievalHit(
                rank=rank,
                score=score,
                bm25_score=bm25_scores[doc_idx],
                embedding_score=embedding_scores[doc_idx],
                record=records[doc_idx],
            )
        )
    return hits

