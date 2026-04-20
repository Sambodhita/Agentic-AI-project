"""
knowledge_base.py — TF-IDF based retrieval system (offline RAG)
Works with: data/legal_documents.json
"""

import json
import pickle
import numpy as np
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


DOCS_FILE = "./data/legal_documents.json"
KB_CACHE = "./knowledge_base/kb_cache.pkl"

_kb = None  # in-memory cache


# ─────────────────────────────────────────────
# LOAD DOCUMENTS
# ─────────────────────────────────────────────
def _load_documents():
    path = Path(DOCS_FILE)
    if not path.exists():
        raise Exception(f"❌ File not found: {DOCS_FILE}")

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ─────────────────────────────────────────────
# BUILD KNOWLEDGE BASE
# ─────────────────────────────────────────────
def _build_kb():
    docs = _load_documents()

    corpus = []
    meta = []

    for doc in docs:
        content = doc.get("content", "")
        title = doc.get("title", "")
        category = doc.get("category", "")
        doc_id = doc.get("id", "")

        # Full document
        corpus.append(content)
        meta.append({
            "title": title,
            "category": category,
            "doc_id": doc_id
        })

        # Chunking (better retrieval)
        words = content.split()
        for i, start in enumerate(range(0, len(words), 80)):
            chunk = " ".join(words[start:start + 80])
            corpus.append(chunk)
            meta.append({
                "title": title,
                "category": category,
                "doc_id": doc_id,
                "chunk": i
            })

    # Vectorization
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=8000
    )

    matrix = vectorizer.fit_transform(corpus)

    # Save cache
    Path("./knowledge_base").mkdir(exist_ok=True)
    kb = {
        "corpus": corpus,
        "meta": meta,
        "vectorizer": vectorizer,
        "matrix": matrix
    }

    with open(KB_CACHE, "wb") as f:
        pickle.dump(kb, f)

    print(f"✅ KB built: {len(corpus)} chunks from {len(docs)} documents")

    return kb


# ─────────────────────────────────────────────
# GET KB (LOAD OR BUILD)
# ─────────────────────────────────────────────
def get_kb():
    global _kb

    if _kb is not None:
        return _kb

    if Path(KB_CACHE).exists():
        with open(KB_CACHE, "rb") as f:
            _kb = pickle.load(f)
        return _kb

    _kb = _build_kb()
    return _kb


# ─────────────────────────────────────────────
# RETRIEVE DOCUMENTS
# ─────────────────────────────────────────────
def retrieve(query: str, n_results: int = 3):
    kb = get_kb()

    q_vec = kb["vectorizer"].transform([query])
    scores = cosine_similarity(q_vec, kb["matrix"])[0]

    top_indices = np.argsort(scores)[::-1]

    results = []
    seen_docs = set()

    for idx in top_indices:
        if scores[idx] < 0.01:
            break

        doc_id = kb["meta"][idx].get("doc_id")

        # Avoid duplicate documents
        if doc_id in seen_docs:
            continue

        seen_docs.add(doc_id)

        results.append({
            "content": kb["corpus"][idx],
            "title": kb["meta"][idx].get("title", ""),
            "category": kb["meta"][idx].get("category", ""),
            "score": round(float(scores[idx]), 3)
        })

        if len(results) >= n_results:
            break

    return results


# ─────────────────────────────────────────────
# GET TITLES (FOR UI)
# ─────────────────────────────────────────────
def get_all_titles():
    docs = _load_documents()
    return [d.get("title", "Untitled") for d in docs]


# ─────────────────────────────────────────────
# TEST RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("🔧 Building / Loading Knowledge Base...\n")

    kb = get_kb()

    print("\n🔍 Test Retrieval:\n")

    results = retrieve("non-compete clause risk unlimited liability")

    for r in results:
        print(f"[{r['score']}] {r['title']}")