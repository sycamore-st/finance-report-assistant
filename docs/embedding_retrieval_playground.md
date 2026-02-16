# Embedding + Retrieval Playground

Use this page to track experiments for embedding choices and retrieval ranking behavior.

## Scripts
- `playground/embedding_retrieval/compare_embeddings.py`
- `playground/embedding_retrieval/compare_retrievers.py`

## Quick commands
```bash
source .venv/bin/activate

python playground/embedding_retrieval/compare_embeddings.py \
  --top-k 5 \
  --output-md docs/embedding_methods_matrix.md

python playground/embedding_retrieval/compare_retrievers.py \
  --top-k 5 \
  --max-queries 30 \
  --output-md docs/retrieval_matrix.md
```

## Matrix columns

### Embedding methods matrix
- `Method`
- `Neighbor Label Overlap@K`
- `Notes`

### Retrieval matrix
- `Retriever`
- `Hit@K`
- `MRR`

## Experiment template

### Experiment: <short-name>
- Date: YYYY-MM-DD
- Goal: what decision this informs
- Data: chunk file path(s)
- Hypothesis: expected outcome before running

### Command
```bash
# paste exact command
```

### Key output
```text
# paste key metrics only
```

### Interpretation
- Which method improved ranking quality?
- Did semantic retrieval help beyond lexical matching?
- Main caveats and failure cases:

### Decision
- Decision: keep / modify / reject approach
- Next code action:

