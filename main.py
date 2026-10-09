"""LegalEase – AI Legal Document Simplifier"""
import os
from pathlib import Path
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from services.gemini_service import simplify_text, ask_question, DISCLAIMER

load_dotenv()
APP_NAME = os.getenv("APP_NAME", "LegalEase")
BASE = Path(__file__).resolve().parent

app = FastAPI(title=APP_NAME)
app.mount("/static", StaticFiles(directory=str(BASE / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request, "app_name": APP_NAME, "disclaimer": DISCLAIMER
    })


@app.post("/simplify", response_class=HTMLResponse)
async def simplify(request: Request, legal_text: str = Form(...)):
    result = simplify_text(legal_text.strip())
    return templates.TemplateResponse("results.html", {
        "request": request, "app_name": APP_NAME,
        "result": result, "legal_text": legal_text, "disclaimer": DISCLAIMER
    })


@app.post("/ask", response_class=HTMLResponse)
async def ask(
    request: Request,
    legal_text: str = Form(...),
    question: str = Form(...),
    prior_summary: str = Form(""),
):
    qa = ask_question(legal_text, question.strip(), prior_summary)
    result = simplify_text(legal_text.strip())  # re-show context
    return templates.TemplateResponse("results.html", {
        "request": request, "app_name": APP_NAME,
        "result": result, "legal_text": legal_text,
        "qa": qa, "disclaimer": DISCLAIMER
    })


@app.get("/health")
async def health():
    return {"status": "ok", "app": APP_NAME, "gemini": bool(os.getenv("GEMINI_API_KEY"))}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=os.getenv("HOST", "0.0.0.0"),
                port=int(os.getenv("PORT", 8000)), reload=True)
