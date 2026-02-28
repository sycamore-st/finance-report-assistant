from __future__ import annotations

import re
from dataclasses import dataclass

from bs4 import BeautifulSoup


@dataclass
class SectionText:
    title: str
    path: str
    text: str


def _normalize_whitespace(text: str) -> str:
    collapsed = re.sub(r"\s+", " ", text)
    return collapsed.strip()


ITEM_HEADING_RE = re.compile(r"^item\s+\d+[a-z]?(?:\.[a-z])?[\.\:]?", re.IGNORECASE)
ITEM_SPLIT_RE = re.compile(r"\b(Item\s+\d+[A-Z]?(?:\.[A-Z])?[\.\:]?)\s+", re.IGNORECASE)


def _is_hidden_tag(tag) -> bool:  # type: ignore[no-untyped-def]
    style = (tag.get("style") or "").lower()
    if "display:none" in style or "visibility:hidden" in style:
        return True

    if (tag.get("aria-hidden") or "").lower() == "true":
        return True

    name = (tag.name or "").lower()
    if name in {"ix:header", "ix:hidden"}:
        return True

    return False


def _is_item_heading(text: str) -> bool:
    if len(text.split()) > 16:
        return False
    return bool(ITEM_HEADING_RE.match(text))


def _split_document_section_by_item(section: SectionText) -> list[SectionText]:
    matches = list(ITEM_SPLIT_RE.finditer(section.text))
    if not matches:
        return [section]

    out: list[SectionText] = []

    # Keep lead-in text before first Item heading.
    first = matches[0]
    lead = _normalize_whitespace(section.text[: first.start()])
    if lead:
        out.append(SectionText(title=section.title, path=section.path, text=lead))

    for idx, match in enumerate(matches):
        start = match.start()
        end = matches[idx + 1].start() if idx + 1 < len(matches) else len(section.text)
        block = _normalize_whitespace(section.text[start:end])
        heading = _normalize_whitespace(match.group(1))
        if not block:
            continue
        out.append(SectionText(title=heading, path=heading, text=block))

    return out or [section]


def extract_sections_from_html(html: str) -> list[SectionText]:
    """Extract readable sections from SEC filing HTML.

    Heuristic strategy for MVP:
    - Remove non-content tags (script/style)
    - Track heading structure (`h1`..`h4`) as section path
    - Collect paragraph/list/table text beneath latest heading
    """
    soup = BeautifulSoup(html, "html.parser")

    # Removes non-content tags (`script`, `style`, `noscript`, `svg`)
    for tag in soup(["script", "style", "noscript", "svg"]):
        tag.decompose()

    # Removes hidden or non-visible elements
    for tag in soup.find_all(_is_hidden_tag):
        tag.decompose()

    sections: list[SectionText] = []
    heading_stack: list[str] = []
    current_title = "Document"
    buffer: list[str] = []

    def flush() -> None:
        nonlocal buffer
        text = _normalize_whitespace("\n".join(buffer))
        if not text:
            buffer = []
            return

        path = " > ".join(heading_stack) if heading_stack else current_title
        sections.append(SectionText(title=current_title, path=path, text=text))
        buffer = []

    # Walks heading/content tags (`h1`-`h4`, `p`, `div`, `li`, `td`, `th`)
    for node in soup.find_all(["h1", "h2", "h3", "h4", "p", "div", "li", "td", "th"]):
        node_text = _normalize_whitespace(node.get_text(" ", strip=True))
        if not node_text:
            continue

        # Tracks heading hierarchy
        if node.name in {"h1", "h2", "h3", "h4"}:
            flush()
            level = int(node.name[1])
            heading_stack[:] = heading_stack[: level - 1]
            heading_stack.append(node_text)
            current_title = node_text
            continue

        # Detects `Item` headings such as `Item 1A. Risk Factors`
        if _is_item_heading(node_text):
            flush()
            heading_stack = [node_text]
            current_title = node_text
            continue

        buffer.append(node_text)

    flush()

    # Splits the “Document” fallback section into section-aware blocks when item headings are found
    if not sections:
        fallback = _normalize_whitespace(soup.get_text(" ", strip=True))
        if fallback:
            sections.append(SectionText(title="Document", path="Document", text=fallback))

    normalized_sections: list[SectionText] = []
    for section in sections:
        if section.title == "Document":
            normalized_sections.extend(_split_document_section_by_item(section))
        else:
            normalized_sections.append(section)

    return normalized_sections
