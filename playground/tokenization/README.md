# Tokenization Playground

Hands-on scripts for understanding tokenizer behavior on SEC filing chunks.

## Run
```bash
source .venv/bin/activate
python playground/tokenization/compare_tokenizers.py --train-ratio 0.8 --min-freq 2
python playground/tokenization/oov_analysis.py --train-ratio 0.8 --min-freq 2
python playground/tokenization/chunk_length_impact.py --budget 220

```

## Optional real BPE
`compare_all_tokenizers.py` will include `hf_bpe` automatically if `tokenizers` is installed.
