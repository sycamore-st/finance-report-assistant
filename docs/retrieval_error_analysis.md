# Retrieval Error Analysis (AAPL 10-K)

Generated: 2026-02-18 11:29:42

Top-K: 5 | Queries: 30

## By Query Type (hybrid)
| Query Type | Hit@K | MRR |
| --- | ---: | ---: |
| general | 0.7600 | 0.5247 |
| growth | 0.5000 | 0.5000 |
| risk | 1.0000 | 0.3333 |

## By Section (hybrid)
| Section | Hit@K | MRR |
| --- | ---: | ---: |
| Document | 0.6667 | 0.4722 |
| Item 1. Business | 0.6429 | 0.3417 |
| Item 12 . | 1.0000 | 1.0000 |
| Item 16. | 1.0000 | 0.7500 |
| Item 1A. Risk Factors | 1.0000 | 0.3333 |
| Item 5. | 1.0000 | 1.0000 |
| Item 7. | 1.0000 | 1.0000 |
| Item 9. | 1.0000 | 1.0000 |
| Item 9C. | 1.0000 | 1.0000 |

## Failure Examples

### bm25
- `q5` (general) expected `74136109c4064fa7` got ['c51679695eb5c9cf', '32c5535f1bfa5205', 'a98fad3bb52c359a', 'c419e50394a6b3f3', '710efa05d290e347']
  - Query: Document report securities registered pursuant
- `q18` (general) expected `3ead5cb56d5b5fb7` got ['4629563380159707', '4332718247216f95', 'e7207b8ecf9df6f4', 'c20ec924bff1388a', '8ec51acbd78174be']
  - Query: Item 1. Business certain services during company
- `q21` (general) expected `6cb0f09f55a152d4` got ['c2ef8fdea73821c0', '74e3538914d50b03', '2a30b0740f107a96', '9b8f5317d00db655', 'ff5250975a52a925']
  - Query: Item 1. Business international trade increase limit
- `q29` (risk) expected `9edc7259b3361505` got ['e7207b8ecf9df6f4', 'bb6b271e637b18f8', 'ae25f11beab21e77', '65190abd74ff8de3', '511d7e7439728ec6']
  - Query: Item 1A. Risk Factors company business results operations
- `q30` (risk) expected `9b8f5317d00db655` got ['e7207b8ecf9df6f4', 'bb6b271e637b18f8', '9edc7259b3361505', 'ae25f11beab21e77', '511d7e7439728ec6']
  - Query: Item 1A. Risk Factors potential outcomes include financial

### embedding
- `q1` (general) expected `32c5535f1bfa5205` got ['b193635aa092eade', 'af08c86fc9894015', '734744bdb7aef076', '36dbcb02503c644c', 'ba5171b529e10e48']
  - Query: Document united states securities exchange
- `q3` (growth) expected `523c27a8aeaa053a` got ['f9e9f1ebe5cf76b3', 'b193635aa092eade', 'af08c86fc9894015', '734744bdb7aef076', '36dbcb02503c644c']
  - Query: Document nasdaq stock market securities
- `q5` (general) expected `74136109c4064fa7` got ['523c27a8aeaa053a', 'b193635aa092eade', 'af08c86fc9894015', '5c5bfd8397469f6c', 'c51679695eb5c9cf']
  - Query: Document report securities registered pursuant
- `q14` (general) expected `04adf9bea77671c8` got ['23f10203fd16f5a0', '68a1de18ed0831b8', 'a54efbd1f2cd0b92', '0a528c4e8ee9678a', 'ba556cf579b89852']
  - Query: Item 1. Business company background designs manufactures
- `q16` (general) expected `f7c54ed981da7421` got ['decfe636560f8318', 'bf9424565561e9f7', '9ac929f03b32f5b5', '7fb96d549a35c932', '87dc8e9245139cc3']
  - Query: Item 1. Business accidental damage theft depending
- `q17` (general) expected `8ec51acbd78174be` got ['f7c54ed981da7421', '6c8c54b01ff78331', '32409801717b66cd', 'b9ddd588091fc917', '1277bc870c0b1ee3']
  - Query: Item 1. Business pacific americas includes north
- `q19` (general) expected `6fb26f38185acd97` got ['23f10203fd16f5a0', 'bf9424565561e9f7', 'a54efbd1f2cd0b92', '9b8f5317d00db655', '33b89a12e9baeda9']
  - Query: Item 1. Business designs develops nearly entire
- `q20` (general) expected `2a30b0740f107a96` got ['68a1de18ed0831b8', 'decfe636560f8318', '736ca5349088b664', '2d051c857f63de33', 'd0bbcc75d09c03b8']
  - Query: Item 1. Business offer integrated solutions company
- `q21` (general) expected `6cb0f09f55a152d4` got ['9b8f5317d00db655', '68a1de18ed0831b8', 'c58d43edc3a7f7b4', 'a3123555c01910c1', '3d3717769fa43829']
  - Query: Item 1. Business international trade increase limit
- `q22` (general) expected `b19107b0130be980` got ['b6a2fce99758b51b', 'decfe636560f8318', '46286bfe29d91538', 'a54efbd1f2cd0b92', '2d051c857f63de33']
  - Query: Item 1. Business limiting company ability obtain

### hybrid_rrf
- `q3` (growth) expected `523c27a8aeaa053a` got ['f9e9f1ebe5cf76b3', '32c5535f1bfa5205', '36dbcb02503c644c', 'c9565da39b000cac', '83efd44e152651fd']
  - Query: Document nasdaq stock market securities
- `q5` (general) expected `74136109c4064fa7` got ['c51679695eb5c9cf', '523c27a8aeaa053a', 'a98fad3bb52c359a', '32c5535f1bfa5205', '710efa05d290e347']
  - Query: Document report securities registered pursuant
- `q16` (general) expected `f7c54ed981da7421` got ['3e137a6a831414f1', 'bf9424565561e9f7', '8092f17acd1780e6', 'decfe636560f8318', 'b3133ce6bb51a963']
  - Query: Item 1. Business accidental damage theft depending
- `q19` (general) expected `6fb26f38185acd97` got ['bf9424565561e9f7', 'b19107b0130be980', 'e7207b8ecf9df6f4', 'ecb29162f54f7c4a', '46286bfe29d91538']
  - Query: Item 1. Business designs develops nearly entire
- `q20` (general) expected `2a30b0740f107a96` got ['736ca5349088b664', '6fb26f38185acd97', '65190abd74ff8de3', 'c2ef8fdea73821c0', 'd0bbcc75d09c03b8']
  - Query: Item 1. Business offer integrated solutions company
- `q21` (general) expected `6cb0f09f55a152d4` got ['9b8f5317d00db655', 'c2ef8fdea73821c0', 'dab62355662c5068', '87dc8e9245139cc3', '30b481a52e650c0c']
  - Query: Item 1. Business international trade increase limit
- `q27` (general) expected `045d4fe310e1082c` got ['0a528c4e8ee9678a', '8092f17acd1780e6', 'decfe636560f8318', '33b89a12e9baeda9', 'cc8d27c8eb3149d8']
  - Query: Item 1. Business company periodically provides certain
