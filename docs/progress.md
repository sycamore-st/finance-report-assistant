# Progress Log

## 2026-02-15
- Initialized repository structure for ingestion/retrieval/qa/classification/summarization modules.
- Added Python packaging (`pyproject.toml`) and CLI entrypoint (`fra`).
- Implemented initial SEC EDGAR ingestion path for one ticker and `10-K` filings.
- Added processing pipeline:
  - SEC HTML cleaning + section extraction
  - Deterministic chunking with overlap
  - `chunks.jsonl` + `chunk_stats.json` outputs
- Added tokenizer/OOV evaluation utility and CLI command.
- Added tests for filing selection, CLI behavior, processing/chunking, and tokenizer metrics.

## 2026-02-16
- Implemented retrieval baseline:
  - BM25 index for lexical relevance
  - Dense hash-embedding index for semantic-ish retrieval
  - Weighted reciprocal rank fusion for hybrid ranking
- Added retrieval CLI commands:
  - `build-retrieval-index`
  - `search`
- Added retrieval tests for index build/load/search and CLI missing-index handling.

## Next
- Grounded Q&A response generation with chunk-level citations.
