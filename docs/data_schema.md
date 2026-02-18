# Data Schema

## Raw Ingestion Layout

`data/raw/sec-edgar/{ticker}/{form}/{accession_no}/`

Files:
- `filing_metadata.json`: normalized metadata for filing selection
- `primary_document.html`: fetched filing document (raw)

## Processed Chunk Layout

`data/processed/chunks/{ticker}/{form}/{accession_no}/`

Files:
- `chunks.jsonl`: cleaned + chunked text with citation metadata
- `chunk_stats.json`: chunking configuration and counts

## Retrieval Index Layout

`data/index/retrieval/{ticker}/{form}/`

Files:
- `manifest.json`: index metadata and source chunk file list
- `records.jsonl`: retrieval corpus records (copied from chunk records)
- `bm25.pkl`: serialized BM25 index
- `embedding.pkl`: serialized dense hash embedding index

## Filing Metadata Fields
- `ticker` (str)
- `cik` (str, 10-digit zero-padded)
- `form` (str)
- `accession_number` (str)
- `filing_date` (str, YYYY-MM-DD)
- `report_date` (str | null)
- `primary_document` (str)
- `primary_doc_description` (str | null)
- `sec_archive_url` (str)

## Chunk Record Fields (`chunks.jsonl`)
- `chunk_id` (str, deterministic hash)
- `chunk_index` (int)
- `ticker` (str)
- `form` (str)
- `cik` (str)
- `accession_number` (str)
- `filing_date` (str)
- `report_date` (str | null)
- `section_title` (str)
- `section_path` (str)
- `char_start` (int)
- `char_end` (int)
- `word_count` (int)
- `text` (str)
- `sentences` (list[str], sentence-level units derived from chunk text)
- `sentence_spans` (list[{text, char_start, char_end}], offsets relative to chunk text)
- `source_file` (str)
- `citation_url` (str)

## Retrieval Hit Fields (`fra search` output)
- `rank` (int)
- `score` (float, fused rank score)
- `bm25_score` (float)
- `embedding_score` (float)
- `chunk_id` (str)
- `ticker` (str)
- `form` (str)
- `accession_number` (str)
- `section_title` (str)
- `citation_url` (str)
- `text` (str)
