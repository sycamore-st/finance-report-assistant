# Streamlit UI (Hugging Face Spaces)

## Local Run

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Hugging Face Space Setup

1. Create a new Space with SDK = `Streamlit`.
2. Push this repository to the Space.
3. Ensure these files exist in repo root:
   - `app.py`
   - `requirements.txt`
4. Set Space secrets/environment variables:
   - `SEC_USER_AGENT=FinanceReportAssistant/0.1 (your-email@example.com)`
   - `HF_PREBUILT_ONLY=1` (recommended for stability/fast startup)
5. Launch/restart the Space.

## Notes
- The app can auto-build ingestion/chunks/index per company on first question.
- Initial run may take time due to SEC fetch and index build.
- For faster demo UX, pre-build and commit index artifacts for selected companies.
- In HF mode (`HF_PREBUILT_ONLY=1`), live build buttons and SEC fetch are disabled.
