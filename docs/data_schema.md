# Data Schema

## Raw Ingestion Layout

`data/raw/sec-edgar/{ticker}/{form}/{accession_no}/`

Files:
- `filing_metadata.json`: normalized metadata for filing selection
- `primary_document.html`: fetched filing document (raw)

## Metadata Fields (current)
- `ticker` (str)
- `cik` (str, 10-digit zero-padded)
- `form` (str)
- `accession_number` (str)
- `filing_date` (str, YYYY-MM-DD)
- `report_date` (str | null)
- `primary_document` (str)
- `primary_doc_description` (str | null)
- `sec_archive_url` (str)
