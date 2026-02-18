from __future__ import annotations

from pathlib import Path

from finance_report_assistant.core.config import settings


def raw_filing_dir(ticker: str, form: str, accession_number: str) -> Path:
    return settings.data_dir / "raw" / "sec-edgar" / ticker.upper() / form / accession_number
