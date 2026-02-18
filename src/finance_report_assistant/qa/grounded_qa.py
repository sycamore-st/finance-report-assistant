from __future__ import annotations

import re
from dataclasses import dataclass

from finance_report_assistant.retrieval.hybrid import RetrievalHit

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass
class Citation:
    chunk_id: str
    citation_url: str
    section_title: str | None
    accession_number: str | None


@dataclass
class QAResult:
    question: str
    answer: str
    citations: list[Citation]


def _split_sentences(text: str) -> list[str]:
    chunks = SENTENCE_RE.split(text.strip())
    return [s.strip() for s in chunks if s.strip()]


def _score_sentence(sentence: str, question_terms: set[str]) -> float:
    sent_terms = set(TOKEN_RE.findall(sentence.lower()))
    overlap = len(question_terms & sent_terms)
    density = overlap / max(1, len(sent_terms))
    return overlap + density


def compose_grounded_answer(
    question: str,
    hits: list[RetrievalHit],
    max_sentences: int = 3,
) -> QAResult:
    if not hits:
        return QAResult(question=question, answer="No relevant evidence was retrieved.", citations=[])

    q_terms = set(TOKEN_RE.findall(question.lower()))
    candidate_sentences: list[tuple[float, str]] = []

    for hit in hits:
        text = hit.record.get("text", "")
        for sentence in _split_sentences(text):
            score = _score_sentence(sentence, q_terms)
            if score > 0:
                candidate_sentences.append((score, sentence))

    if candidate_sentences:
        top = sorted(candidate_sentences, key=lambda x: x[0], reverse=True)[:max_sentences]
        answer = " ".join(sentence for _, sentence in top)
    else:
        answer = _split_sentences(hits[0].record.get("text", ""))[0] if hits[0].record.get("text") else "No answerable evidence found."

    citations: list[Citation] = []
    for hit in hits[:max_sentences]:
        citations.append(
            Citation(
                chunk_id=str(hit.record.get("chunk_id", "")),
                citation_url=str(hit.record.get("citation_url", "")),
                section_title=hit.record.get("section_title"),
                accession_number=hit.record.get("accession_number"),
            )
        )

    return QAResult(question=question, answer=answer, citations=citations)
