from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import quote

from finance_report_assistant.retrieval.hybrid import RetrievalHit

SENTENCE_RE = re.compile(r"(?<=[.!?])\s+")
TOKEN_RE = re.compile(r"[a-z0-9]+")


@dataclass
class Citation:
    chunk_id: str
    citation_url: str
    section_title: str | None
    accession_number: str | None
    citation_highlight_url: str | None = None
    sec_text_url: str | None = None
    filing_index_url: str | None = None
    search_hint: str | None = None
    evidence_snippet: str | None = None
    evidence_sentences: list[str] | None = None


@dataclass
class QAResult:
    question: str
    answer: str
    citations: list[Citation]


def _split_sentences(text: str) -> list[str]:
    chunks = SENTENCE_RE.split(text.strip())
    return [s.strip() for s in chunks if s.strip()]


def _score_sentence(sentence: str, question_terms: set[str]) -> float:
    """Scores candidate sentences by term overlap and overlap density"""
    sent_terms = set(TOKEN_RE.findall(sentence.lower()))
    overlap = len(question_terms & sent_terms)
    density = overlap / max(1, len(sent_terms))
    return overlap + density


def _evidence_sentences_from_record(record: dict, question_terms: set[str], top_n: int = 2) -> list[str]:
    candidates = record.get("sentences") or []
    if not candidates:
        candidates = _split_sentences(record.get("text", ""))

    scored: list[tuple[float, str]] = []
    for sent in candidates:
        if not sent:
            continue
        score = _score_sentence(sent, question_terms)
        if score > 0:
            scored.append((score, sent.strip()))

    if scored:
        top = sorted(scored, key=lambda x: x[0], reverse=True)[:top_n]
        return [s for _, s in top]

    return [candidates[0].strip()] if candidates else []


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
        record = hit.record
        accession_number = record.get("accession_number")
        cik = record.get("cik")
        sec_text_url: str | None = None
        if accession_number and cik:
            accession_no_dashes = str(accession_number).replace("-", "")
            filing_base = (
                f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/"
                f"{accession_no_dashes}"
            )
            sec_text_url = (
                f"{filing_base}/{accession_no_dashes}.txt"
            )
            filing_index_url = f"{filing_base}/{accession_number}-index.html"
        else:
            filing_index_url = None

        evidence_sentences = _evidence_sentences_from_record(record, q_terms, top_n=2)
        evidence_text = " ".join(evidence_sentences).strip() if evidence_sentences else str(record.get("text", "")).strip()
        search_hint = " ".join(evidence_text.split()[:10]) if evidence_text else None
        evidence_snippet = evidence_text[:260] if evidence_text else None
        highlight_url: str | None = None
        if record.get("citation_url") and evidence_sentences:
            highlight_text = evidence_sentences[0][:180].strip()
            if highlight_text:
                highlight_url = f"{record['citation_url']}#:~:text={quote(highlight_text, safe='')}"

        citations.append(
            Citation(
                chunk_id=str(record.get("chunk_id", "")),
                citation_url=str(record.get("citation_url", "")),
                citation_highlight_url=highlight_url,
                section_title=record.get("section_title"),
                accession_number=accession_number,
                sec_text_url=sec_text_url,
                filing_index_url=filing_index_url,
                search_hint=search_hint,
                evidence_snippet=evidence_snippet,
                evidence_sentences=evidence_sentences,
            )
        )

    return QAResult(question=question, answer=answer, citations=citations)
