from __future__ import annotations

import json
from pathlib import Path

from finance_report_assistant.core.models import FilingMetadata
from finance_report_assistant.ingestion.sec_client import SEC_ARCHIVES_BASE, SecEdgarClient
from finance_report_assistant.utils.paths import raw_filing_dir

# Small starter mapping for MVP. Expand as needed.
TICKER_TO_CIK = {
    "AAPL": "0000320193",
    "MSFT": "0000789019",
    "GOOGL": "0001652044",
    "AMZN": "0001018724",
    "META": "0001326801",
}


def _iter_recent_filings(submissions: dict, form: str):
    recent = submissions.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    accession_numbers = recent.get("accessionNumber", [])
    filing_dates = recent.get("filingDate", [])
    report_dates = recent.get("reportDate", [])
    primary_documents = recent.get("primaryDocument", [])
    primary_doc_descriptions = recent.get("primaryDocDescription", [])

    for idx, recent_form in enumerate(forms):
        if recent_form != form:
            continue
        yield {
            "accession_number": accession_numbers[idx],
            "filing_date": filing_dates[idx],
            "report_date": report_dates[idx] if idx < len(report_dates) else None,
            "primary_document": primary_documents[idx],
            "primary_doc_description": (
                primary_doc_descriptions[idx] if idx < len(primary_doc_descriptions) else None
            ),
        }


def ingest_filings_for_ticker(
    ticker: str,
    form: str = "10-K",
    limit: int = 1,
    client: SecEdgarClient | None = None,
) -> list[Path]:
    ticker_up = ticker.upper()
    if ticker_up not in TICKER_TO_CIK:
        raise ValueError(f"Ticker '{ticker}' is not in MVP allowlist: {sorted(TICKER_TO_CIK)}")

    cik = TICKER_TO_CIK[ticker_up]

    owns_client = client is None
    sec_client = client or SecEdgarClient()
    written_paths: list[Path] = []

    try:
        submissions = sec_client.get_submissions(cik)
        picked = list(_iter_recent_filings(submissions, form=form))[:limit]

        for filing in picked:
            accession_number = filing["accession_number"]
            primary_document = filing["primary_document"]
            archive_url = (
                f"{SEC_ARCHIVES_BASE}/{int(cik)}/{accession_number.replace('-', '')}/{primary_document}"
            )

            metadata = FilingMetadata(
                ticker=ticker_up,
                cik=cik,
                form=form,
                accession_number=accession_number,
                filing_date=filing["filing_date"],
                report_date=filing.get("report_date"),
                primary_document=primary_document,
                primary_doc_description=filing.get("primary_doc_description"),
                sec_archive_url=archive_url,
            )

            html = sec_client.get_archive_document(cik, accession_number, primary_document)

            out_dir = raw_filing_dir(ticker_up, form, accession_number)
            out_dir.mkdir(parents=True, exist_ok=True)

            metadata_path = out_dir / "filing_metadata.json"
            metadata_path.write_text(metadata.model_dump_json(indent=2), encoding="utf-8")

            html_path = out_dir / "primary_document.html"
            html_path.write_text(html, encoding="utf-8")

            manifest_path = out_dir / "manifest.json"
            manifest = {
                "ticker": ticker_up,
                "form": form,
                "accession_number": accession_number,
                "files": [metadata_path.name, html_path.name],
            }
            manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            written_paths.append(out_dir)

        return written_paths
    finally:
        if owns_client:
            sec_client.close()
