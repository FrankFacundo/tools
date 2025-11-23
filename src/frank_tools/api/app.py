"""FastAPI application for Frank tools."""

from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel

from frank_tools.translate.google_free import GoogleTranslate

app = FastAPI(title="Frank tools", version="0.1.0")
translator = GoogleTranslate()


class TranslateRequest(BaseModel):
    text: str
    sl: str = "auto"
    tl: str = "en"


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/translate")
async def translate(req: TranslateRequest) -> dict[str, str]:
    result = translator.translate(req.text, sl=req.sl, tl=req.tl)
    return {"translation": result["translation"], "src_lang": result["src_lang"] or "unknown"}
