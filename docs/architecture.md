# Architecture

## MVP Scope (Phase 1)
- Source: SEC EDGAR official endpoints only
- Ingestion target: `10-K` filings for up to 5 tickers
- Output: raw filing metadata + primary filing document persisted locally

## Planned Modules
- `ingestion`: EDGAR submissions + filing fetch
- `core`: shared config and data models
- `utils`: low-level helpers (paths, logging)
- `retrieval`: BM25 + embedding indexers and search APIs
- `qa`: grounded answer generation with citation stitching
- `classification`: financial theme/risk classifier
- `summarization`: section and document summarization
- `api`: local app/API surface
