import json
from typing import List, Dict


def load_docs(path: str = "data/legal_docs.json") -> List[Dict]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            docs = json.load(f)

    except FileNotFoundError:
        raise Exception(f"❌ File not found: {path}")

    except json.JSONDecodeError:
        raise Exception("❌ Invalid JSON format")

    # Validate structure
    if not isinstance(docs, list):
        raise Exception("❌ JSON must be a list of documents")

    validated_docs = []

    for i, doc in enumerate(docs):

        # Check required fields
        if not all(k in doc for k in ["id", "title", "content"]):
            raise Exception(f"❌ Missing fields in document index {i}")

        # Check types
        if not isinstance(doc["id"], str):
            raise Exception(f"❌ 'id' must be string in doc {i}")

        if not isinstance(doc["title"], str):
            raise Exception(f"❌ 'topic' must be string in doc {i}")

        if not isinstance(doc["content"], str):
            raise Exception(f"❌ 'text' must be string in doc {i}")

        # Check length (important for capstone)
        if len(doc["text"].split()) < 20:
            print(f" Warning: Document {doc['id']} is too short (<20 words)")

        validated_docs.append(doc)

    print(f" Loaded {len(validated_docs)} documents successfully")

    return validated_docs
if __name__ == "__main__":
    docs = load_docs()
    print(f"Loaded {len(docs)} documents")
    print(docs[0])