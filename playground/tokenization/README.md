# Tokenization Playground

Hands-on scripts for understanding tokenizer behavior on SEC filing chunks.

## Run
```bash
source .venv/bin/activate
python playground/tokenization/compare_tokenizers.py --chunks <path-to-chunks.jsonl>
python playground/tokenization/oov_analysis.py --chunks <path-to-chunks.jsonl>
python playground/tokenization/chunk_length_impact.py --chunks <path-to-chunks.jsonl>
```
