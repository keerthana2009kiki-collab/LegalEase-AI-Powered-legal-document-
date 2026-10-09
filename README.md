# LegalEase – AI Legal Text Simplifier

Paste legal text → **plain-English summary**, clause breakdown, **red flags**, and Q&A (Gemini).

**Not legal advice** — educational only.

## Run (Windows)

```cmd
cd LegalEase
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Set `GEMINI_API_KEY` in `.env`, then:

```cmd
python main.py
```

http://127.0.0.1:8000
