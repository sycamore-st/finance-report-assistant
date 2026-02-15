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

## Next
- Retrieval baseline: BM25 + embedding index.
- Grounded Q&A response generation with chunk-level citations.
