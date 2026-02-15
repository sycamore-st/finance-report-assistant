# Finance Report Assistant

Implementation-first MVP for SEC EDGAR ingestion, retrieval, and grounded Q&A.

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

## MVP Demo (current: ingestion only)

Ingest one ticker and one filing type (`10-K`):

```bash
fra ingest-10k --ticker AAPL --limit 1
```

Outputs are written under `data/raw/sec-edgar/<ticker>/10-K/`.

## Roadmap status

- [x] Repo skeleton
- [x] Initial EDGAR ingestion (`10-K`, one ticker)
- [ ] Cleaning + chunking + schema
- [ ] Retrieval baseline (BM25 + embeddings)
- [ ] Grounded Q&A with citations
- [ ] Theme classification
- [ ] Summarization
- [ ] Evaluation suite
