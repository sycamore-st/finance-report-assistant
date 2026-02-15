from __future__ import annotations

import hashlib
from dataclasses import dataclass

from src.finance_report_assistant.processing.html_cleaner import SectionText


@dataclass
class ChunkCandidate:
    section_title: str
    section_path: str
    text: str


def _chunk_words(words: list[str], max_words: int, overlap_words: int) -> list[tuple[int, int, str]]:
    if max_words <= 0:
        raise ValueError("max_words must be positive")
    if overlap_words < 0:
        raise ValueError("overlap_words cannot be negative")
    if overlap_words >= max_words:
        raise ValueError("overlap_words must be less than max_words")

    chunks: list[tuple[int, int, str]] = []
    step = max_words - overlap_words
    start = 0

    while start < len(words):
        end = min(start + max_words, len(words))
        text = " ".join(words[start:end]).strip()
        chunks.append((start, end, text))
        if end == len(words):
            break
        start += step

    return chunks


def build_chunk_candidates(
    sections: list[SectionText],
    max_words: int = 220,
    overlap_words: int = 40,
    min_words: int = 20,
) -> list[ChunkCandidate]:
    if min_words <= 0:
        raise ValueError("min_words must be positive")

    candidates: list[ChunkCandidate] = []

    for section in sections:
        words = section.text.split()
        if not words:
            continue

        section_chunks = _chunk_words(words, max_words=max_words, overlap_words=overlap_words)
        for _, _, chunk_text in section_chunks:
            chunk_word_count = len(chunk_text.split())
            if chunk_word_count < min_words:
                continue
            candidates.append(
                ChunkCandidate(
                    section_title=section.title,
                    section_path=section.path,
                    text=chunk_text,
                )
            )

    return candidates


def deterministic_chunk_id(accession_number: str, section_path: str, text: str) -> str:
    key = f"{accession_number}|{section_path}|{text}".encode("utf-8")
    return hashlib.sha1(key).hexdigest()[:16]
