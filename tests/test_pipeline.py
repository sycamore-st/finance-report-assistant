import json
from pathlib import Path

from finance_report_assistant.core.config import settings
from finance_report_assistant.processing.pipeline import build_chunks_for_filing_dir


def test_build_chunks_for_filing_dir_writes_jsonl(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "data_dir", tmp_path / "data")
    filing_dir = tmp_path / "AAPL" / "10-K" / "0001"
    filing_dir.mkdir(parents=True)

    metadata = {
        "ticker": "AAPL",
        "form": "10-K",
        "cik": "0000320193",
        "accession_number": "0000000000-00-000001",
        "filing_date": "2025-11-01",
        "report_date": "2025-09-30",
        "primary_document": "report.htm",
        "sec_archive_url": "https://www.sec.gov/Archives/edgar/data/320193/000000000000000001/report.htm",
    }
    (filing_dir / "filing_metadata.json").write_text(json.dumps(metadata), encoding="utf-8")
    (filing_dir / "primary_document.html").write_text(
        "<html><body><h1>Item 1</h1><p>alpha beta gamma delta epsilon</p></body></html>",
        encoding="utf-8",
    )

    output_path = build_chunks_for_filing_dir(filing_dir, max_words=3, overlap_words=1, min_words=1)

    assert output_path.exists()
    lines = output_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) >= 2

    first = json.loads(lines[0])
    assert first["ticker"] == "AAPL"
    assert first["form"] == "10-K"
    assert first["citation_url"].startswith("https://www.sec.gov/Archives/edgar/data")
    assert first["chunk_id"]
