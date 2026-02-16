from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]


def resolve_repo_path(path: Path) -> Path:
    if path.is_absolute():
        return path
    cwd_candidate = (Path.cwd() / path).resolve()
    if cwd_candidate.exists():
        return cwd_candidate
    return (REPO_ROOT / path).resolve()


def load_chunk_records(chunks_path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line in chunks_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        row = json.loads(line)
        if row.get("text"):
            records.append(row)
    return records


def load_chunk_texts(chunks_path: Path) -> list[str]:
    return [row["text"] for row in load_chunk_records(chunks_path)]

