# Finance Report Assistant

Implementation-first MVP for SEC EDGAR ingestion, retrieval, and grounded Q&A.

## Quickstart (`.venv`)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

## Current MVP commands

Ingest one ticker and one filing type (`10-K`):

```bash
fra ingest-10k --ticker AAPL --limit 1
```

Build cleaned/chunked outputs:

```bash
fra build-chunks --ticker AAPL --form 10-K --limit 1
```

Run tokenizer/OOV evaluation for chunks:

```bash
fra eval-tokenizer \
  --chunks data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl
```

Outputs:
- Raw: `data/raw/sec-edgar/<ticker>/10-K/<accession>/`
- Processed chunks: `data/processed/chunks/<ticker>/<form>/<accession>/chunks.jsonl`

Build retrieval index (BM25 + dense hash embeddings):

```bash
fra build-retrieval-index --ticker AAPL --form 10-K --limit 1
```

Run hybrid retrieval query:

```bash
fra search --ticker AAPL --form 10-K --query "What supply chain risks are disclosed?" --top-k 5
```

Index artifacts:
- `data/index/retrieval/<ticker>/<form>/manifest.json`
- `data/index/retrieval/<ticker>/<form>/records.jsonl`
- `data/index/retrieval/<ticker>/<form>/bm25.pkl`
- `data/index/retrieval/<ticker>/<form>/embedding.pkl`

## Roadmap status

- [x] Repo skeleton
- [x] Initial EDGAR ingestion (`10-K`, one ticker)
- [x] Cleaning + chunking + metadata schema
- [x] Tokenizer/OOV evaluation script
- [x] Retrieval baseline (BM25 + embeddings)
- [ ] Grounded Q&A with citations
- [ ] Theme classification
- [ ] Summarization
- [ ] Evaluation suite expansion
