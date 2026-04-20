from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

PROJECT_DIR = Path(__file__).resolve().parents[1]
SOURCE_DIR = PROJECT_DIR / "legal_docs"
OUTPUT_PATH = PROJECT_DIR / "data" / "legal_documents.json"


@dataclass
class SourceText:
    title: str
    source_name: str
    source_type: str
    text: str


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def read_txt(path: Path) -> SourceText:
    text = path.read_text(encoding="utf-8")
    return SourceText(
        title=path.stem,
        source_name=path.name,
        source_type="text",
        text=clean_text(text),
    )


def read_docx(path: Path) -> SourceText:
    with zipfile.ZipFile(path) as archive:
        xml = archive.read("word/document.xml").decode("utf-8", errors="ignore")
    xml = re.sub(r"</w:p>", "\n", xml)
    xml = re.sub(r"<[^>]+>", "", xml)
    return SourceText(
        title=path.stem,
        source_name=path.name,
        source_type="docx",
        text=clean_text(xml),
    )


def chunk_words(text: str, chunk_size: int = 200, overlap: int = 40) -> Iterable[str]:
    words = text.split()
    chunks = []

    start = 0
    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = max(end - overlap, start + 1)

    return chunks


def discover_sources() -> list[SourceText]:
    discovered = []

    for path in SOURCE_DIR.glob("*"):
        if path.suffix == ".txt":
            discovered.append(read_txt(path))

        elif path.suffix == ".docx":
            discovered.append(read_docx(path))

    return discovered


def build_documents():
    sources = discover_sources()
    documents = []
    doc_id = 1

    for source in sources:
        for idx, chunk in enumerate(chunk_words(source.text), start=1):
            documents.append(
                {
                    "id": f"legal_{doc_id:03d}",
                    "topic": f"{source.title} | Part {idx}",
                    "text": chunk,
                    "source_name": source.source_name,
                    "source_type": source.source_type,
                }
            )
            doc_id += 1

    return documents


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    docs = build_documents()

    OUTPUT_PATH.write_text(
        json.dumps(docs, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    print(f"✅ Built {len(docs)} legal documents → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()