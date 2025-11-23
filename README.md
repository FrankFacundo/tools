# Frank tools

Frank tools is a small, production-ready Python toolkit that bundles a few practical utilities:

- Google Drive file downloader that works with share links.
- Lightweight translation helper that wraps the public Google translate endpoint.
- M4B chapter-aware splitter helper for audio workflows.
- HTTP API (FastAPI) exposing health and translation endpoints.
- CLI commands and Docker image for easy usage.

## Installation

```bash
pip install .
```

## CLI usage

- Download from Drive: `frank-tools-drive --link "<drive url>"`
- Translate: `frank-tools-translate --text "Hola" --tl en`
- M4B split helper: `frank-tools-m4b --input book.m4b --chapters chapters.txt --output ./out`
- Central CLI with subcommands: `frank-tools <subcommand>`

## HTTP API

Run locally:

```bash
uvicorn frank_tools.api.app:app --reload
```

Endpoints:

- `GET /health` – health check.
- `POST /translate` – translate a piece of text via the internal translator.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[test]"
```

Run tests:

```bash
pytest
```

Build & publish:

```bash
pip install build twine
python -m build
twine upload dist/*
```

## Docker

```bash
docker build -t frank-tools .
docker run -p 8000:8000 frank-tools
```

## VS Code tips

- See `.vscode/launch.json` for debugging uvicorn or `pytest -k "pattern"`.
- `.vscode/settings.json` points the Python analysis engine at `src/` to resolve imports.
