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


class FilingChunk(BaseModel):
    chunk_id: str
    ticker: str
    form: str
    cik: str
    accession_number: str
    filing_date: str
    report_date: str | None = None
    section_title: str
    section_path: str
    char_start: int
    char_end: int
    word_count: int
    text: str
    source_file: str
    citation_url: HttpUrl
