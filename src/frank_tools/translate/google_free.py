"""Lightweight Google Translate helper."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import requests


@dataclass
class TranslationResult:
    translation: str
    original: str
    src_lang: Optional[str]
    alternatives: List[str]
    raw: Any


class GoogleTranslate:
    """
    Minimal wrapper around the unofficial Google translate JSON endpoint.
    """

    def __init__(self, host: str = "translate.googleapis.com", https: bool = True):
        self.scheme = "https" if https else "http"
        self.host = host
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0", "Accept": "*/*"})

    @staticmethod
    def build_request_url(
        text: str, sl: str = "auto", tl: str = "en", hl: Optional[str] = None, no_autocorrect: bool = False, scheme: str = "https", host: str = "translate.googleapis.com"
    ) -> str:
        """Pure helper used for testing; builds the translate endpoint URL."""
        hl = hl or tl
        qc = "qc" if no_autocorrect else "qca"
        return (
            f"{scheme}://{host}/translate_a/single?client=gtx"
            f"&ie=UTF-8&oe=UTF-8"
            f"&dt=bd&dt=ex&dt=ld&dt=md&dt=rw&dt=rm&dt=ss&dt=t&dt=at&dt=gt"
            f"&dt={qc}"
            f"&sl={quote(sl)}&tl={quote(tl)}&hl={quote(hl)}"
            f"&q={quote(text)}"
        )

    def _request_url(self, text: str, sl: str = "auto", tl: str = "en", hl: Optional[str] = None, no_autocorrect: bool = False) -> str:
        return self.build_request_url(text, sl=sl, tl=tl, hl=hl, no_autocorrect=no_autocorrect, scheme=self.scheme, host=self.host)

    @staticmethod
    def parse_translation_payload(data: Any, fallback_text: str) -> TranslationResult:
        """
        Parse the JSON payload returned by Google into a structured result.
        """
        segments = data[0] or []
        translated_chunks = [seg[0] for seg in segments if seg and seg[0] is not None]
        original_chunks = [seg[1] for seg in segments if seg and len(seg) > 1 and seg[1] is not None]

        translation = "".join(translated_chunks)
        original = "".join(original_chunks) or fallback_text

        src_lang = data[2] if len(data) > 2 and isinstance(data[2], str) else None

        alternatives: List[str] = []
        if len(data) > 5 and isinstance(data[5], list):
            for entry in data[5]:
                if isinstance(entry, list) and len(entry) > 2 and isinstance(entry[2], list):
                    for alt in entry[2]:
                        if isinstance(alt, list) and alt and isinstance(alt[0], str):
                            alternatives.append(alt[0])
        # remove duplicates preserving order
        alternatives = list(dict.fromkeys(alternatives))

        return TranslationResult(
            translation=translation,
            original=original,
            src_lang=src_lang,
            alternatives=alternatives,
            raw=data,
        )

    def translate(self, text: str, sl: str = "auto", tl: str = "en", hl: Optional[str] = None, no_autocorrect: bool = False) -> Dict[str, Any]:
        url = self._request_url(text, sl=sl, tl=tl, hl=hl, no_autocorrect=no_autocorrect)
        response = self.session.get(url, timeout=20)
        response.raise_for_status()
        data = response.json()
        parsed = self.parse_translation_payload(data, fallback_text=text)
        return {
            "translation": parsed.translation,
            "original": parsed.original,
            "src_lang": parsed.src_lang,
            "alternatives": parsed.alternatives,
            "raw": parsed.raw,
        }

    def tts_url(self, text: str, tl: str = "en") -> str:
        return f"{self.scheme}://{self.host}/translate_tts?ie=UTF-8&client=gtx&tl={quote(tl)}&q={quote(text)}"

    def web_translate_url(self, url_to_translate: str, sl: str = "auto", tl: str = "en", hl: Optional[str] = None) -> str:
        hl = hl or tl
        return f"https://translate.google.com/translate?hl={quote(hl)}&sl={quote(sl)}&tl={quote(tl)}&u={quote(url_to_translate)}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Translate text using the unofficial Google translate endpoint.")
    parser.add_argument("--text", type=str, required=True, help="Text to translate")
    parser.add_argument("--sl", type=str, default="auto", help="Source language (default: auto)")
    parser.add_argument("--tl", type=str, default="en", help="Target language (default: en)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    translator = GoogleTranslate()
    result = translator.translate(args.text, sl=args.sl, tl=args.tl)
    print(result["translation"])


if __name__ == "__main__":
    main()
