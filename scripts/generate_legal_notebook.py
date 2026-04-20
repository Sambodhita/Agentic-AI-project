from __future__ import annotations

import json
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parents[1]
OUTPUT_PATH = PROJECT_DIR / "legal_capstone.ipynb"

DATA_PATH = PROJECT_DIR / "data" / "legal_documents.json"
DOC_COUNT = len(json.loads(DATA_PATH.read_text(encoding="utf-8"))) if DATA_PATH.exists() else 0


def md_cell(text: str):
    return {
        "cell_type": "markdown",
        "metadata": {},
        "source": [line + "\n" for line in text.strip().splitlines()],
    }


def code_cell(text: str):
    return {
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [line + "\n" for line in text.strip().splitlines()],
    }


def build_notebook():
    cells = [

        md_cell(f"""
# LegalAI Assistant — Capstone Project

An AI-powered legal assistant using LangGraph, RAG, and evaluation.

---

## What It Does

- Answers legal questions from documents
- Uses retrieval (RAG)
- Maintains conversation memory
- Uses tools (calculations / planning)
- Evaluates answer faithfulness

---

##  Knowledge Base

Total documents: **{DOC_COUNT}**
"""),

        code_cell("""
from agent import build_legal_assistant, ask

bundle = build_legal_assistant()

question = "Explain contract law basics"
response = ask(bundle, question)

print(response)
"""),

        md_cell("""
##  Testing

Test:
- Legal queries
- Tool queries
- Memory queries
- Edge cases
"""),

        md_cell("""
## Deployment

Run:

streamlit run capstone_streamlit.py
"""),

    ]

    return {
        "cells": cells,
        "metadata": {
            "kernelspec": {"name": "python3"},
            "language_info": {"name": "python"},
        },
        "nbformat": 4,
        "nbformat_minor": 5,
    }


def main():
    notebook = build_notebook()
    OUTPUT_PATH.write_text(json.dumps(notebook, indent=2), encoding="utf-8")
    print(f"Notebook created → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()