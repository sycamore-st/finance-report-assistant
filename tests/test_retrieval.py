import json
from pathlib import Path

from finance_report_assistant.core.config import settings
from finance_report_assistant.retrieval.index import (
    build_retrieval_index,
    default_index_dir,
    load_retrieval_index,
)


def _write_chunks_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = "\n".join(json.dumps(r) for r in rows) + "\n"
    path.write_text(payload, encoding="utf-8")


def test_build_and_search_retrieval_index(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")

    chunk_file = (
        settings.data_dir
        / "processed"
        / "chunks"
        / "AAPL"
        / "10-K"
        / "0001"
        / "chunks.jsonl"
    )
    rows = [
        {
            "chunk_id": "c1",
            "ticker": "AAPL",
            "form": "10-K",
            "accession_number": "0001",
            "section_title": "Item 1A. Risk Factors",
            "citation_url": "https://www.sec.gov/a1",
            "text": "Supply chain disruptions and component shortages could harm margins.",
        },
        {
            "chunk_id": "c2",
            "ticker": "AAPL",
            "form": "10-K",
            "accession_number": "0001",
            "section_title": "Liquidity",
            "citation_url": "https://www.sec.gov/a2",
            "text": "Cash flow and liquidity remain strong with substantial marketable securities.",
        },
        {
            "chunk_id": "c3",
            "ticker": "AAPL",
            "form": "10-K",
            "accession_number": "0001",
            "section_title": "Growth",
            "citation_url": "https://www.sec.gov/a3",
            "text": "Growth in services and AI-enabled products increased revenue.",
        },
    ]
    _write_chunks_jsonl(chunk_file, rows)

    index_dir, manifest = build_retrieval_index(ticker="AAPL", form="10-K", limit=1)
    assert index_dir == default_index_dir("AAPL", "10-K")
    assert manifest["record_count"] == 3
    assert (index_dir / "bm25.pkl").exists()
    assert (index_dir / "embedding.pkl").exists()
    assert (index_dir / "records.jsonl").exists()

    index = load_retrieval_index(index_dir)
    hits = index.search("What supply chain risks are described?", top_k=2)

    assert len(hits) == 2
    assert hits[0].record["chunk_id"] == "c1"
    assert hits[0].record["citation_url"] == "https://www.sec.gov/a1"

