# Tokenization Playground

Use this page to track experiments tied to real SEC chunk data.

## Default Data Source
- `data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl`

## Scripts
- `playground/tokenization/compare_tokenizers.py`
- `playground/tokenization/oov_analysis.py`
- `playground/tokenization/chunk_length_impact.py`
- `playground/tokenization/compare_all_tokenizers.py`

## Quick Commands
```bash
source .venv/bin/activate

python playground/tokenization/compare_tokenizers.py \
  --train-ratio 0.8 --min-freq 2 \
  --output-md docs/tokenizer_matrix.md

python playground/tokenization/oov_analysis.py \
  --train-ratio 0.8 --min-freq 2

python playground/tokenization/chunk_length_impact.py \
  --budget 220


```

## Matrix Columns
- `Tokenizer`
- `OOV`
- `Avg Seq Len`
- `Vocab Size`
- `Strength`
- `Weakness`

## Experiment Template

### Experiment: <short-name>
- Date: YYYY-MM-DD
- Goal: what decision this should inform
- Data: chunk file path(s)
- Hypothesis: expected outcome before running

### Command
```bash
# paste exact command
```

### Key Output
```text
# paste key metrics only
```

### Interpretation
- What changed across tokenizers?
- Which tokenizer best matches our retrieval/QA goals?
- Risks or caveats:

### Decision
- Decision: keep / modify / reject approach
- Next action in code:
