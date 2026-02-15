| Tokenizer | OOV | Avg Seq Len | Vocab Size | Strength | Weakness |
| --- | ---: | ---: | ---: | --- | --- |
| whitespace | 0.3189 | 204.36 | 3161 | Fast baseline | Poor punctuation handling |
| regex | 0.1719 | 263.03 | 2570 | Stronger word boundary handling | Language-specific heuristics |
| simple_subword | 0.1201 | 329.66 | 2591 | Lower OOV than word-level | Toy method, not production-grade |
| punct_aware | 0.1217 | 270.27 | 2521 | Clean punctuation splitting | Still brittle for multilingual text |
| normalized_whitespace | 0.3189 | 204.36 | 3161 | Unicode/case normalization | Can lose case-sensitive signals |
| char_no_space | 0.0022 | 1101.16 | 60 | No OOV | Very long sequences |
| char_keep_space | 0.0019 | 1304.52 | 61 | Preserves whitespace cues | Longest sequences |
| char_3gram | 0.0621 | 1302.52 | 5101 | Captures morphology/robustness | Large token counts |
| byte_level | 0.0019 | 1315.34 | 91 | No OOV across languages | Very long sequences, less interpretable |
| vocab_unk | 0.0000 | 263.03 | 2571 | Explicit OOV/UNK behavior | Information loss on unknown terms |
