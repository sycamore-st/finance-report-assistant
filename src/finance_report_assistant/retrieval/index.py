from __future__ import annotations

import json
import pickle
from dataclasses import dataclass
from pathlib import Path

from src.finance_report_assistant.core.config import settings
from src.finance_report_assistant.retrieval.bm25 import BM25Index
from src.finance_report_assistant.retrieval.corpus import discover_chunk_files, load_chunk_records
from src.finance_report_assistant.retrieval.embedding import HashEmbeddingIndex
from src.finance_report_assistant.retrieval.hybrid import RetrievalHit, fuse_rankings


@dataclass
class RetrievalIndex:
    records: list[dict]
    bm25: BM25Index
    embedding: HashEmbeddingIndex

    def search(
        self,
        query: str,
        top_k: int = 5,
        bm25_weight: float = 0.55,
        embedding_weight: float = 0.45,
    ) -> list[RetrievalHit]:
        bm25_scores = self.bm25.scores(query)
        emb_scores = self.embedding.scores(query)
        return fuse_rankings(
            records=self.records,
            bm25_scores=bm25_scores,
            embedding_scores=emb_scores,
            top_k=top_k,
            bm25_weight=bm25_weight,
            embedding_weight=embedding_weight,
        )


def default_index_dir(ticker: str, form: str) -> Path:
    return settings.data_dir / "index" / "retrieval" / ticker.upper() / form


def build_retrieval_index(
    ticker: str,
    form: str = "10-K",
    limit: int | None = None,
    embedding_dim: int = 384,
    out_dir: Path | None = None,
) -> tuple[Path, dict]:
    chunk_files = discover_chunk_files(ticker=ticker, form=form, limit=limit)
    if not chunk_files:
        raise FileNotFoundError(f"No chunk files found for {ticker.upper()} {form}")

    records = load_chunk_records(chunk_files)
    if not records:
        raise ValueError("Chunk files loaded but no text records were found")

    texts = [r["text"] for r in records]
    bm25 = BM25Index.fit(texts)
    embedding = HashEmbeddingIndex.fit(texts, dim=embedding_dim)
    index = RetrievalIndex(records=records, bm25=bm25, embedding=embedding)

    output_dir = out_dir or default_index_dir(ticker=ticker, form=form)
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "records.jsonl").write_text(
        "\n".join(json.dumps(r, ensure_ascii=False) for r in records) + "\n",
        encoding="utf-8",
    )
    with (output_dir / "bm25.pkl").open("wb") as f:
        pickle.dump(index.bm25, f)
    with (output_dir / "embedding.pkl").open("wb") as f:
        pickle.dump(index.embedding, f)

    manifest = {
        "ticker": ticker.upper(),
        "form": form,
        "record_count": len(records),
        "chunk_files": [str(p) for p in chunk_files],
        "embedding": {
            "type": "hashing",
            "dim": embedding_dim,
        },
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    return output_dir, manifest


def load_retrieval_index(index_dir: Path) -> RetrievalIndex:
    records: list[dict] = []
    for line in (index_dir / "records.jsonl").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        records.append(json.loads(line))

    with (index_dir / "bm25.pkl").open("rb") as f:
        bm25: BM25Index = pickle.load(f)
    with (index_dir / "embedding.pkl").open("rb") as f:
        embedding: HashEmbeddingIndex = pickle.load(f)

    return RetrievalIndex(records=records, bm25=bm25, embedding=embedding)

