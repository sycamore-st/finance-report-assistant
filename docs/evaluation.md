# Evaluation

## Initial Plan
- Ingestion correctness checks (metadata integrity, URL validity, file persistence)
- Retrieval quality metrics: Recall@k / MRR (planned)
- Q&A grounding checks: citation coverage and citation precision (planned)
- Classification metrics: per-label precision/recall/F1 (planned)
- Summarization quality: factual consistency + section coverage (planned)

## Tokenizer/OOV Eval - 2026-02-15 16:04:11
- Source: `data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl`
- Chunks: 2
- Total tokens: 6
- Avg tokens/chunk: 3.0
- Min tokens/chunk: 3
- Max tokens/chunk: 3
- Unique tokens: 5
- Rare-token ratio (freq <= 2): 1.0

## Tokenizer/OOV Eval - 2026-02-15 16:06:23
- Source: `data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl`
- Chunks: 238
- Total tokens: 48638
- Avg tokens/chunk: 204.36
- Min tokens/chunk: 20
- Max tokens/chunk: 220
- Unique tokens: 4944
- Rare-token ratio (freq <= 2): 0.0725

## Tokenizer/OOV Eval - 2026-02-15 16:37:43
- Source: `/Users/claire/PycharmProjects/finance-report-assistant/data/processed/chunks/AAPL/10-K/0000320193-25-000079/chunks.jsonl`
- Chunks: 238
- Total tokens: 48638
- Avg tokens/chunk: 204.36
- Min tokens/chunk: 20
- Max tokens/chunk: 220
- Unique tokens: 4944
- Rare-token ratio (freq <= 2): 0.0725
