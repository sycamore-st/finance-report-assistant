from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from finance_report_assistant.classification.themes import classify_themes
from finance_report_assistant.ingestion.edgar_ingest import (
    TICKER_TO_CIK,
    TICKER_TO_NAME,
    ingest_filings_for_ticker,
)
from finance_report_assistant.processing.pipeline import build_chunks_for_ticker_form
from finance_report_assistant.qa.grounded_qa import compose_grounded_answer
from finance_report_assistant.retrieval.index import (
    build_retrieval_index,
    default_index_dir,
    load_retrieval_index,
)
from finance_report_assistant.summarization.extractive import summarize_chunks

FORMS = ["10-K"]
EXAMPLE_QUESTIONS = [
    "What supply chain risks are disclosed?",
    "What does the filing say about liquidity and cash flow?",
    "What are the major growth drivers mentioned?",
    "What guidance or outlook language is included?",
    "How does management describe macroeconomic risks?",
    "What are the key legal or regulatory risk disclosures?",
    "What is said about capital allocation and share repurchases?",
    "What are the main segment or geographic revenue drivers?",
    "What does the filing say about debt and financing capacity?",
    "What cybersecurity or operational risks are highlighted?",
]


def _inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,700&family=Instrument+Sans:wght@400;500;600&display=swap');

        :root {
          --surface: #f7f4ef;
          --surface-2: #f3eee6;
          --ink: #141413;
          --muted: #706b62;
          --line: #d6cec2;
          --accent: #6e7f76;
        }

        .block-container {
          max-width: 1040px;
          padding-top: 1.25rem;
          padding-bottom: 2rem;
        }

        h1, h2, h3 {
          font-family: "Fraunces", Georgia, serif;
          color: var(--ink);
          letter-spacing: -0.02em;
          line-height: 1.05;
        }

        p, div, label, textarea, input, button {
          font-family: "Instrument Sans", "Avenir Next", sans-serif !important;
          font-size: 14px;
        }

        span {
          font-family: inherit;
        }

        /* Keep Streamlit/Material icon glyphs working */
        [data-testid="collapsedControl"] span,
        .material-symbols-rounded,
        .material-icons {
          font-family: "Material Symbols Rounded", "Material Icons", sans-serif !important;
        }

        .hero {
          border: 1px solid var(--line);
          background: var(--surface);
          border-radius: 14px;
          padding: 16px 18px;
          margin-bottom: 12px;
        }

        .hero-title {
          font-size: 30px;
          margin: 0;
          line-height: 1.05;
        }

        .hero-sub {
          margin-top: 4px;
          color: var(--muted);
          font-size: 13px;
        }

        .panel {
          border: 1px solid var(--line);
          background: var(--surface-2);
          border-radius: 12px;
          padding: 12px 14px;
          margin-bottom: 10px;
        }

        .answer {
          border-left: 3px solid var(--accent);
        }

        .pill {
          display: inline-block;
          padding: 4px 10px;
          border-radius: 999px;
          font-size: 11px;
          border: 1px solid var(--line);
          background: #fff;
          margin-right: 8px;
          margin-bottom: 8px;
          color: #49443d;
        }

        .cite-title {
          font-weight: 600;
          margin-bottom: 6px;
        }

        .quote {
          border-left: 2px solid #9aa89f;
          padding: 4px 0 4px 10px;
          margin: 6px 0;
          color: #242321;
          font-size: 13px;
        }

        div[data-testid="stSidebar"] h2, div[data-testid="stSidebar"] h3,
        div[data-testid="stSidebar"] label,
        div[data-testid="stSidebar"] p,
        div[data-testid="stSidebar"] span {
          font-family: "Instrument Sans", sans-serif;
          letter-spacing: 0;
          font-size: 13px !important;
        }

        .stButton>button {
          border-radius: 10px;
          border: 1px solid #6e7f76;
          background: #768880;
          color: white;
          font-weight: 600;
          font-size: 13px;
        }

        .stButton>button:hover {
          background: #687a72;
          border-color: #687a72;
        }

        .stDownloadButton>button {
          border-radius: 10px;
          border: 1px solid var(--line);
          background: #fff;
          color: #2d2a24;
          font-size: 13px;
        }

        #MainMenu, footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


def _index_ready(index_dir: Path) -> bool:
    required = ["manifest.json", "records.jsonl", "bm25.pkl", "embedding.pkl"]
    return index_dir.exists() and all((index_dir / f).exists() for f in required)


def _build_pipeline(ticker: str, form: str, limit: int = 1) -> None:
    ingest_filings_for_ticker(ticker=ticker, form=form, limit=limit)
    build_chunks_for_ticker_form(ticker=ticker, form=form, limit=limit)
    build_retrieval_index(ticker=ticker, form=form, limit=limit)


def _run_qa(ticker: str, form: str, question: str, top_k: int) -> dict:
    index = load_retrieval_index(default_index_dir(ticker=ticker, form=form))
    hits = index.search(question, top_k=top_k)

    if not hits:
        return {
            "answer": "No retrieval hits found.",
            "summary": "",
            "themes": [],
            "citations": [],
            "hits": [],
        }

    qa = compose_grounded_answer(question, hits)
    summary = summarize_chunks([h.record for h in hits], max_sentences=4)
    top_text = "\n".join(h.record.get("text", "") for h in hits)
    themes = [
        {"theme": t.theme, "score": round(t.score, 6), "hits": t.hits}
        for t in classify_themes(top_text)
        if t.hits > 0
    ]

    citations = [
        {
            "chunk_id": c.chunk_id,
            "citation_url": c.citation_url,
            "citation_highlight_url": c.citation_highlight_url,
            "section_title": c.section_title,
            "evidence_sentences": c.evidence_sentences,
            "evidence_snippet": c.evidence_snippet,
        }
        for c in qa.citations
    ]

    hits_payload = [
        {
            "rank": h.rank,
            "score": round(h.score, 6),
            "section_title": h.record.get("section_title"),
            "chunk_id": h.record.get("chunk_id"),
            "citation_url": h.record.get("citation_url"),
            "text": h.record.get("text", "")[:700],
        }
        for h in hits
    ]

    return {
        "answer": qa.answer,
        "summary": summary,
        "themes": themes,
        "citations": citations,
        "hits": hits_payload,
    }


def main() -> None:
    st.set_page_config(
        page_title="Finance Report Assistant",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    _inject_styles()

    st.markdown(
        """
        <div class="hero">
          <h1 class="hero-title">Finance Report Assistant</h1>
          <div class="hero-sub">Grounded answers over SEC filings with direct source evidence.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    with st.expander("How This Tool Works", expanded=False):
        st.markdown(
            """
            **What this tool does**
            - Pulls official SEC EDGAR filing content (currently `10-K`).
            - Chunks and indexes filing text for retrieval.
            - Answers your question using retrieved evidence.
            - Returns citations with quoted source sentences.

            **How to use**
            1. Select a company and filing form from the sidebar.
            2. Choose an example question or type your own.
            3. Click **Ask**.
            4. Open citation links to verify evidence in source filing HTML.

            **Good question style**
            - Use focused prompts such as “liquidity risks”, “growth drivers”, “guidance outlook”.
            - Keep one objective per question for cleaner evidence retrieval.
            """
        )

    with st.sidebar:
        st.subheader("Workspace")
        tickers = sorted(TICKER_TO_CIK.keys())
        ticker = st.selectbox(
            "Company",
            tickers,
            index=0,
            format_func=lambda t: f"{TICKER_TO_NAME.get(t, t)} ({t})",
        )
        form = st.selectbox("Form", FORMS, index=0)
        top_k = st.slider("Top-K", min_value=1, max_value=10, value=5)
        auto_build = st.checkbox("Auto-build if missing", value=True)

        st.markdown("---")
        st.subheader("Prompt")
        selected_example = st.selectbox("Example", EXAMPLE_QUESTIONS, index=0)

    question = st.text_area("Question", value=selected_example, height=92)

    left, right = st.columns([1, 1])
    with left:
        if st.button("Build / Refresh", use_container_width=True):
            with st.spinner(f"Building pipeline for {ticker} {form}..."):
                _build_pipeline(ticker=ticker, form=form, limit=1)
            st.success("Pipeline ready.")

    with right:
        ask_clicked = st.button("Ask", use_container_width=True)

    if ask_clicked:
        if not question.strip():
            st.error("Enter a question first.")
            st.stop()

        index_dir = default_index_dir(ticker=ticker, form=form)
        if not _index_ready(index_dir):
            if not auto_build:
                st.error(f"Index missing at {index_dir}. Enable auto-build or run Build / Refresh.")
                st.stop()
            with st.spinner(f"Index missing. Building for {ticker} {form}..."):
                _build_pipeline(ticker=ticker, form=form, limit=1)

        with st.spinner("Retrieving evidence and composing answer..."):
            result = _run_qa(ticker=ticker, form=form, question=question, top_k=top_k)

        st.subheader("Answer")
        st.markdown(f'<div class="panel answer">{result["answer"]}</div>', unsafe_allow_html=True)

        if result["summary"]:
            st.subheader("Summary")
            st.markdown(f'<div class="panel">{result["summary"]}</div>', unsafe_allow_html=True)

        st.subheader("Themes")
        if result["themes"]:
            pill_html = "".join(
                f'<span class="pill">{t["theme"]}: {t["score"]:.4f}</span>'
                for t in result["themes"]
            )
            st.markdown(f'<div class="panel">{pill_html}</div>', unsafe_allow_html=True)
        else:
            st.info("No strong theme signals in top evidence.")

        st.subheader("Citations")
        if result["citations"]:
            for c in result["citations"]:
                link = c.get("citation_highlight_url") or c["citation_url"]
                st.markdown(
                    f'<div class="panel"><div class="cite-title">{c.get("section_title") or "Unknown section"} · '
                    f'<code>{c["chunk_id"]}</code> · <a href="{link}" target="_blank">source html</a></div></div>',
                    unsafe_allow_html=True,
                )

                evidence = c.get("evidence_sentences") or []
                if not evidence and c.get("evidence_snippet"):
                    evidence = [c["evidence_snippet"]]
                for sentence in evidence:
                    st.markdown(f'<div class="quote">"{sentence}"</div>', unsafe_allow_html=True)
        else:
            st.info("No citations found.")

        with st.expander("Retrieved Chunks"):
            for h in result["hits"]:
                st.markdown(
                    f'**Rank {h["rank"]}** · score `{h["score"]}` · '
                    f'{h.get("section_title") or "Unknown"} · `{h.get("chunk_id")}`'
                )
                st.write(h["text"])
                st.markdown(f'[source]({h["citation_url"]})')
                st.markdown("---")

        st.download_button(
            "Download JSON",
            data=json.dumps(result, ensure_ascii=False, indent=2),
            file_name=f"qa_{ticker}_{form}.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
