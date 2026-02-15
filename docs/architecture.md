# Architecture

## MVP Scope (Phase 1)
- Source: SEC EDGAR official endpoints only
- Ingestion target: `10-K` filings for up to 5 tickers
- Output: raw filing metadata + primary filing document persisted locally
- Processing target: cleaned, section-aware chunks with citation metadata

## Current Data Flow
1. `ingest-10k`: SEC submissions JSON -> select matching filing -> fetch archive document
2. `build-chunks`: parse filing HTML -> extract sections -> chunk text -> write `chunks.jsonl`
3. `eval-tokenizer`: compute token-length and OOV proxy stats -> append Markdown report

## Module Boundaries
- `ingestion`: EDGAR submissions + filing fetch
- `processing`: HTML cleaning, chunking, tokenizer/OOV evaluation
- `core`: shared config and data models
- `utils`: helpers (paths)
- `retrieval`: BM25 + embedding indexers and search APIs (planned)
- `qa`: grounded answer generation with citation stitching (planned)
- `classification`: financial theme/risk classifier (planned)
- `summarization`: section and document summarization (planned)
- `api`: local app/API surface (planned)
