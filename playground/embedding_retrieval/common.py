from __future__ import annotations

import re
import sys
from pathlib import Path

DEFAULT_CHUNKS = Path("data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl")
REPO_ROOT = Path(__file__).resolve().parents[2]
TOKEN_RE = re.compile(r"[a-z0-9]+")

try:
    from finance_report_assistant.utils.chunks import (
        load_chunk_records as _shared_load_chunk_records,
        resolve_repo_path as _shared_resolve_repo_path,
    )
except ModuleNotFoundError:
    sys.path.insert(0, str(REPO_ROOT / "src"))
    from finance_report_assistant.utils.chunks import (
        load_chunk_records as _shared_load_chunk_records,
        resolve_repo_path as _shared_resolve_repo_path,
    )


def resolve_chunks_path(chunks_path: Path) -> Path:
    return _shared_resolve_repo_path(chunks_path)


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(text.lower())


def load_chunk_records(chunks_path: Path) -> list[dict]:
    return _shared_load_chunk_records(chunks_path)


def build_lightweight_eval_queries(records: list[dict], max_queries: int = 30) -> list[dict]:
    """
    Build self-supervised query/target pairs for quick retrieval experiments.
    Query text combines section title + a few salient terms from chunk text.
    """
    queries: list[dict] = []
    for idx, row in enumerate(records[:max_queries]):
        text_tokens = tokenize(row["text"])
        unique_terms: list[str] = []
        for tok in text_tokens:
            if len(tok) < 5:
                continue
            if tok in unique_terms:
                continue
            unique_terms.append(tok)
            if len(unique_terms) >= 4:
                break

        section = row.get("section_title", "").strip()
        query_text = f"{section} {' '.join(unique_terms)}".strip()
        if not query_text:
            continue

        queries.append(
            {
                "query_id": f"q{idx + 1}",
                "query": query_text,
                "target_chunk_id": row.get("chunk_id"),
            }
        )
    return queries
