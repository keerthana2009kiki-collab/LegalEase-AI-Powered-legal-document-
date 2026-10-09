"""LegalEase – Gemini service for legal text simplification."""
import os, json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
MODEL = "gemini-1.5-flash"

DISCLAIMER = (
    "This is for educational understanding only. "
    "It is NOT legal advice and does not replace a qualified lawyer."
)


def _parse(text: str):
    text = text.strip()
    if "```json" in text:
        s = text.find("```json") + 7
        e = text.find("```", s)
        text = text[s:e].strip()
    elif "```" in text:
        s = text.find("```") + 3
        e = text.find("```", s)
        text = text[s:e].strip()
    try:
        return json.loads(text)
    except Exception:
        start, end = text.find("{"), text.rfind("}") + 1
        if start >= 0 and end > start:
            try:
                return json.loads(text[start:end])
            except Exception:
                pass
        return None


def simplify_text(legal_text: str) -> dict:
    prompt = f"""You are LegalEase, an educational assistant that explains legal language in plain English.
You are NOT a lawyer. Always keep explanations educational.

Legal text:
\"\"\"
{legal_text[:6000]}
\"\"\"

Respond ONLY with JSON:
{{
  "summary": "plain English overview of the whole text",
  "clauses": [
    {{"title": "short title", "plain_english": "what it means", "original_snippet": "short quote"}}
  ],
  "red_flags": ["possible risk or thing to watch", "..."],
  "key_obligations": ["obligation 1", "obligation 2"],
  "disclaimer": "{DISCLAIMER}"
}}
"""
    if not API_KEY:
        return _fallback(legal_text)
    try:
        model = genai.GenerativeModel(MODEL)
        r = model.generate_content(prompt)
        data = _parse(r.text) or _fallback(legal_text)
        data["disclaimer"] = DISCLAIMER
        data["generated_at"] = datetime.utcnow().isoformat() + "Z"
        data["is_fallback"] = False
        return data
    except Exception as e:
        d = _fallback(legal_text)
        d["error"] = str(e)
        return d


def ask_question(legal_text: str, question: str, prior_summary: str = "") -> dict:
    prompt = f"""You are LegalEase (educational only, NOT a lawyer).
Original text (excerpt):
\"\"\"
{legal_text[:4000]}
\"\"\"
Prior summary: {prior_summary[:1500]}

User question: {question}

Answer in plain English. Be clear this is educational, not legal advice.
Respond ONLY with JSON:
{{
  "question": "{question}",
  "answer": "plain English answer",
  "disclaimer": "{DISCLAIMER}"
}}
"""
    if not API_KEY:
        return {
            "question": question,
            "answer": "Demo mode: set GEMINI_API_KEY for live answers. Generally, early exit terms depend on the contract — this is not legal advice.",
            "disclaimer": DISCLAIMER,
            "is_fallback": True,
        }
    try:
        model = genai.GenerativeModel(MODEL)
        r = model.generate_content(prompt)
        data = _parse(r.text) or {
            "question": question,
            "answer": r.text[:800] if r.text else "Could not generate answer.",
            "disclaimer": DISCLAIMER,
        }
        data["disclaimer"] = DISCLAIMER
        data["is_fallback"] = False
        return data
    except Exception as e:
        return {
            "question": question,
            "answer": f"Error: {e}",
            "disclaimer": DISCLAIMER,
            "is_fallback": True,
        }


def _fallback(legal_text: str) -> dict:
    snippet = (legal_text or "No text")[:120]
    return {
        "summary": f"Demo summary of the provided text starting with: “{snippet}…”. Set GEMINI_API_KEY for live AI simplification.",
        "clauses": [
            {
                "title": "Main clause (demo)",
                "plain_english": "This is a placeholder explanation. With a Gemini API key, each important part of the document is explained in everyday language.",
                "original_snippet": snippet,
            }
        ],
        "red_flags": [
            "Demo mode — real red-flag detection needs GEMINI_API_KEY",
            "Always read the full original document",
        ],
        "key_obligations": ["Review the full agreement carefully", "Ask a lawyer for formal advice"],
        "disclaimer": DISCLAIMER,
        "is_fallback": True,
        "generated_at": datetime.utcnow().isoformat() + "Z",
    }
