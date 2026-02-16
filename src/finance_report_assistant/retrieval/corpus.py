from __future__ import annotations

from pathlib import Path

from finance_report_assistant.core.config import settings
from finance_report_assistant.utils.chunks import load_chunk_records as _load_chunk_records


def discover_chunk_files(ticker: str, form: str = "10-K", limit: int | None = None) -> list[Path]:
    root = settings.data_dir / "processed" / "chunks" / ticker.upper() / form
    if not root.exists():
        return []

    filing_dirs = sorted([p for p in root.iterdir() if p.is_dir()])
    if limit is not None:
        filing_dirs = filing_dirs[:limit]

    out: list[Path] = []
    for filing_dir in filing_dirs:
        chunks_path = filing_dir / "chunks.jsonl"
        if chunks_path.exists():
            out.append(chunks_path)
    return out


def load_chunk_records(chunk_files: list[Path]) -> list[dict]:
    records: list[dict] = []
    for chunk_file in chunk_files:
        records.extend(_load_chunk_records(chunk_file))
    return records
