# Embedding + Retrieval Playground

Hands-on scripts for learning embedding concepts and retrieval behavior on SEC filing chunks.

## Why this exists
- Step 4 gave tokenizer/OOV intuition.
- This playground extends that to:
  - embedding representations (sparse vs dense-ish)
  - retrieval ranking quality (BM25 vs embedding vs hybrid)

## Concepts (quick mapping)
- **Word embeddings**: map words/text to vectors where nearby vectors imply similar meaning/use.
- **Word2Vec (CBOW / Skip-gram)**: learns local-context semantics from prediction tasks.
- **GloVe**: learns vectors from global co-occurrence statistics.
- In this project MVP, we use:
  - BM25 for lexical precision
  - hash-based dense vectors for lightweight semantic retrieval

## Run
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

## Default data source
- `data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl`

## Notes
- Retrieval metrics here are lightweight (`Hit@K`, `MRR`) using auto-generated query/target pairs.
- This is for learning and directional comparison, not final benchmark reporting.

