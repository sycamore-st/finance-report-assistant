# Finance Report Assistant

Implementation-first MVP for SEC EDGAR ingestion, retrieval, and grounded Q&A.

## Quickstart (`.venv`)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
cp .env.example .env
```

## Core commands

Ingest one ticker and one filing type (`10-K`):

```bash
fra ingest-10k --ticker AAPL --limit 1
```

Build cleaned/chunked outputs:

```bash
fra build-chunks --ticker AAPL --form 10-K --limit 1
```

Build retrieval index:

```bash
fra build-retrieval-index --ticker AAPL --form 10-K --limit 1
```

Ask grounded question with citations/themes/summary:

```bash
fra ask --ticker AAPL --form 10-K --question "What supply chain risks are disclosed?" --top-k 5
```


Evaluate retrieval quality and write summary + error analysis docs:

```bash
fra eval-retrieval --ticker AAPL --form 10-K --top-k 5 --max-queries 30
```

## Streamlit UI

Live demo: [Hugging Face Space](https://huggingface.co/spaces/wu-yanjing/finance-report-assistant)

Run local UI:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

UI features:
- company selection with full names (`AAPL/MSFT/GOOGL/AMZN/META/NVDA/TSLA/JPM/JNJ/XOM`)
- example question presets + custom input
- grounded answer with citations + summary + theme scores
- in-app quick manual: what the tool does and how to use it

For Hugging Face deployment details, see `docs/streamlit_hf.md`.

## Unified MVP demo flow

Single command to ingest filings, build chunks/index, and return answer + citations:

```bash
fra demo --ticker AAPL --question "What supply chain risks are disclosed?" --limit 1
```

## Output locations
- Raw: `data/raw/sec-edgar/<ticker>/10-K/<accession>/`
- Processed chunks: `data/processed/chunks/<ticker>/<form>/<accession>/chunks.jsonl`
- Retrieval index: `data/index/retrieval/<ticker>/<form>/`

## Roadmap status

- [x] Repo skeleton
- [x] Initial EDGAR ingestion (`10-K`, one ticker)
- [x] Cleaning + chunking + metadata schema
- [x] Tokenizer/OOV evaluation script
- [x] Retrieval baseline (BM25 + embeddings)
- [x] Grounded Q&A with citations (extractive MVP)
- [x] Theme classification (keyword baseline)
- [x] Summarization (extractive baseline)
- [ ] Evaluation suite expansion / error analysis depth
