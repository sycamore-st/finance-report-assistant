import json
from pathlib import Path

from finance_report_assistant.core.config import settings
from finance_report_assistant.evaluation.retrieval_eval import (
    evaluate_retrieval,
    render_error_analysis_markdown,
    render_summary_markdown,
)
from finance_report_assistant.retrieval.index import build_retrieval_index, load_retrieval_index


def _write_chunks_jsonl(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in rows) + "\n", encoding="utf-8")


def test_evaluate_retrieval_and_markdown(tmp_path: Path, monkeypatch) -> None:
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
            "citation_url": "https://sec.gov/c1",
            "text": "Supply chain disruptions and litigation risks could harm margins.",
        },
        {
            "chunk_id": "c2",
            "ticker": "AAPL",
            "form": "10-K",
            "accession_number": "0001",
            "section_title": "Liquidity",
            "citation_url": "https://sec.gov/c2",
            "text": "Cash flow and liquidity are strong with low debt and high capital reserves.",
        },
        {
            "chunk_id": "c3",
            "ticker": "AAPL",
            "form": "10-K",
            "accession_number": "0001",
            "section_title": "Growth",
            "citation_url": "https://sec.gov/c3",
            "text": "Growth in services and market demand increased revenue outlook.",
        },
    ]
    _write_chunks_jsonl(chunk_file, rows)

    index_dir, _ = build_retrieval_index(ticker="AAPL", form="10-K", limit=1)
    index = load_retrieval_index(index_dir)

    payload = evaluate_retrieval(index, top_k=2, max_queries=3, error_limit=5)

    assert payload["query_count"] > 0
    assert len(payload["results"]) == 3
    assert "best_weight" in payload
    assert "errors" in payload

    summary = render_summary_markdown(payload, ticker="AAPL", form="10-K")
    detail = render_error_analysis_markdown(payload, ticker="AAPL", form="10-K")

    assert "Retriever" in summary
    assert "Retrieval Error Analysis" in detail
