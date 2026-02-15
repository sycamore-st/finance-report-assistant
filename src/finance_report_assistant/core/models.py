from __future__ import annotations

from pydantic import BaseModel, HttpUrl


class FilingMetadata(BaseModel):
    ticker: str
    cik: str
    form: str
    accession_number: str
    filing_date: str
    report_date: str | None = None
    primary_document: str
    primary_doc_description: str | None = None
    sec_archive_url: HttpUrl
