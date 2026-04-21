
"""
Legal Assistant Agent (Final)

Capabilities:
1. Graph-based orchestration (LangGraph)
2. RAG (ChromaDB + embeddings)
3. Memory (thread-based)
4. Self-evaluation loop
5. Tools (deadline, risk, math)
6. Interface (ask function)
"""

import chromadb
from sentence_transformers import SentenceTransformer
from langchain_openai import ChatOpenAI

from legal_assistant.graph import build_graph
from data.loader import load_docs


#  LLM
from langchain_groq import ChatGroq
import streamlit as st

llm = ChatGroq(
    model="llama3-8b-8192",
    temperature=0,
    api_key=st.secrets["legalAI"]
)

#  EMBEDDINGS
embedder = SentenceTransformer("all-MiniLM-L6-v2")


# LOAD DOCUMENTS
docs = load_docs()


#  VECTOR DATABASE (ChromaDB)
client = chromadb.Client()

# Avoid duplicate collection error
try:
    collection = client.get_collection("legal_kb")
except:
    collection = client.create_collection(name="legal_kb")

# Add documents (only if empty)
if collection.count() == 0:
    for doc in docs:
        embedding = embedder.encode(doc["content"]).tolist()

        collection.add(
            documents=[doc["content"]],
            embeddings=[embedding],
            ids=[doc["id"]],
            metadatas=[{"topic": doc["title"]}]
        )


#  BUILD GRAPH
app = build_graph(llm, collection,embedder)


# MAIN INTERFACE (Capability 6)
def ask(question: str, thread_id: str = "default") -> str:
    """
    Main function to interact with the agent
    """

    state = {
        "question": question,
        "messages": [],
        "route": "",
        "retrieved": "",
        "sources": [],
        "tool_result": "",
        "answer": "",
        "faithfulness": 0.0,
        "eval_retries": 0,
        "user_name": ""
    }

    result = app.invoke(
        state,
        {"configurable": {"thread_id": thread_id}}
    )

    return result["answer"]

def chat(user_message: str, thread_id: str = "default") -> dict:
    response = ask(user_message, thread_id)

    return {
        "response": response,
        "intent": "unknown",
        "eval_passed": True,
        "sources": [],
        "thread_id": thread_id
    }

#  TEST RUN
if __name__ == "__main__":

    print(" Legal Assistant Running...\n")

    test_questions = [
        "What is a contract?",
        "Calculate penalty 1000 at 10%",
        "Analyze risk unlimited liability clause",
        "What happens in breach of contract?",
        "Hello, my name is Neha",
        "What is my name?"
    ]

    for q in test_questions:
        print(f"\n Q: {q}")
        print(f" A: {ask(q)}")
