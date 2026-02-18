from __future__ import annotations

import json
from pathlib import Path

from finance_report_assistant.core.config import settings
from finance_report_assistant.core.models import FilingChunk
from finance_report_assistant.processing.chunker import build_chunk_candidates, deterministic_chunk_id
from finance_report_assistant.processing.html_cleaner import extract_sections_from_html
from finance_report_assistant.processing.sentences import split_sentences_with_spans


def _processed_chunk_dir(ticker: str, form: str, accession_number: str) -> Path:
    return (
        settings.data_dir
        / "processed"
        / "chunks"
        / ticker.upper()
        / form
        / accession_number
    )


def build_chunks_for_filing_dir(
    filing_dir: Path,
    max_words: int = 220,
    overlap_words: int = 40,
    min_words: int = 20,
) -> Path:
    metadata_path = filing_dir / "filing_metadata.json"
    html_path = filing_dir / "primary_document.html"

    if not metadata_path.exists() or not html_path.exists():
        raise FileNotFoundError(f"Missing required ingestion files in {filing_dir}")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    html = html_path.read_text(encoding="utf-8", errors="ignore")

    sections = extract_sections_from_html(html)
    candidates = build_chunk_candidates(
        sections,
        max_words=max_words,
        overlap_words=overlap_words,
        min_words=min_words,
    )

    chunk_dir = _processed_chunk_dir(
        metadata["ticker"],
        metadata["form"],
        metadata["accession_number"],
    )
    chunk_dir.mkdir(parents=True, exist_ok=True)

    chunks_path = chunk_dir / "chunks.jsonl"

    char_cursor = 0
    lines: list[str] = []
    for idx, candidate in enumerate(candidates):
        chunk_id = deterministic_chunk_id(
            metadata["accession_number"],
            candidate.section_path,
            candidate.text,
        )
        char_start = char_cursor
        char_end = char_start + len(candidate.text)

        sentence_spans = split_sentences_with_spans(candidate.text)
        sentences = [s["text"] for s in sentence_spans if s.get("text")]

        row = FilingChunk(
            chunk_id=chunk_id,
            ticker=metadata["ticker"],
            form=metadata["form"],
            cik=metadata["cik"],
            accession_number=metadata["accession_number"],
            filing_date=metadata["filing_date"],
            report_date=metadata.get("report_date"),
            section_title=candidate.section_title,
            section_path=candidate.section_path,
            char_start=char_start,
            char_end=char_end,
            word_count=len(candidate.text.split()),
            text=candidate.text,
            source_file=str(html_path),
            citation_url=metadata["sec_archive_url"],
            sentences=sentences,
            sentence_spans=sentence_spans,
        )
        char_cursor = char_end + 1

        payload = row.model_dump(mode="json")
        payload["chunk_index"] = idx
        lines.append(json.dumps(payload, ensure_ascii=False))

    chunks_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")

    stats = {
        "ticker": metadata["ticker"],
        "form": metadata["form"],
        "accession_number": metadata["accession_number"],
        "chunk_count": len(lines),
        "max_words": max_words,
        "overlap_words": overlap_words,
        "min_words": min_words,
        "output_file": str(chunks_path),
    }
    (chunk_dir / "chunk_stats.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")

    return chunks_path


def build_chunks_for_ticker_form(
    ticker: str,
    form: str = "10-K",
    max_words: int = 220,
    overlap_words: int = 40,
    min_words: int = 20,
    limit: int | None = None,
) -> list[Path]:
    raw_root = settings.data_dir / "raw" / "sec-edgar" / ticker.upper() / form
    if not raw_root.exists():
        return []

    filing_dirs = sorted([p for p in raw_root.iterdir() if p.is_dir()])
    if limit is not None:
        filing_dirs = filing_dirs[:limit]

    outputs: list[Path] = []
    for filing_dir in filing_dirs:
        outputs.append(
            build_chunks_for_filing_dir(
                filing_dir=filing_dir,
                max_words=max_words,
                overlap_words=overlap_words,
                min_words=min_words,
            )
        )

    return outputs
