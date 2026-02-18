# Progress Log

## 2026-02-15
- Initialized repository structure for ingestion/retrieval/qa/classification/summarization modules.
- Added Python packaging (`pyproject.toml`) and CLI entrypoint (`fra`).
- Implemented SEC EDGAR ingestion for one ticker and `10-K` filings.
- Added processing pipeline:
  - SEC HTML cleaning + section extraction
  - Deterministic chunking with overlap
  - `chunks.jsonl` + `chunk_stats.json` outputs
- Added tokenizer/OOV evaluation utility and CLI command.
- Added retrieval baseline:
  - BM25 index
  - hash-based embedding index
  - hybrid fusion retrieval
- Added grounded QA/classification/summarization baseline:
  - `fra ask` returns answer + citations + themes + summary
  - `fra demo` unifies ingest -> chunk -> index -> answer in one command

## Next
- Expand evaluation suite with retrieval error analysis slices.
- Replace heuristic QA/summarization with model-backed generation while preserving citations.
