# Agentic-AI-project

# Legal Assistant

An AI-based system for analyzing, drafting, and understanding legal documents.

---

## About the Project

Legal Assistant is an agentic AI system built to handle common legal document tasks such as analysis, drafting, and risk assessment.

It uses a structured workflow and combines multiple components like retrieval, memory, and simple tools to produce more reliable responses.

This project is designed as a capstone to demonstrate practical use of agentic AI concepts.

---

## Features

* Analyze legal documents to extract key information
* Generate basic legal drafts like agreements and NDAs
* Answer legal-related questions
* Provide simple risk assessment with suggestions
* Maintain conversation context using memory

---

## How It Works

The system follows a step-by-step workflow:

1. The user submits a query
2. The system identifies the type of task
3. Relevant information is retrieved from a small knowledge base
4. Additional tools are used if needed
5. A response is generated
6. The response is evaluated before returning
7. Conversation is stored for future context

---

## Architecture

```
User Query
   ↓
Router
   ↓
Retriever (ChromaDB)
   ↓
Tool Layer
   ↓
Response Generation
   ↓
Evaluation
   ↓
Memory (thread_id)
```

---

## Tech Stack

* LangGraph (workflow management)
* ChromaDB (vector database)
* Sentence Transformers (embeddings)
* FastAPI (backend API)
* Streamlit (UI)
* Python

---

## Project Structure

```
legal-assistant/
│
├── agent.py
├── vectorstore.py
├── tools.py
├── api.py
├── app.py
├── index.html
└── docs/
    └── documentation.pdf
```

---

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the Streamlit app:

```bash
streamlit run app.py
```

Run the API:

```bash
uvicorn api:api --reload
```

---

## Example Uses

* Analyze a contract for missing clauses
* Draft a simple agreement
* Ask questions about legal terms
* Check risk level in a document

---

## Limitations

* Requires an API key for full functionality
* Knowledge base is limited to a small set of documents
* Not a substitute for professional legal advice

---

## Future Improvements

* Add more legal documents to the knowledge base
* Improve evaluation of responses
* Support document uploads
* Enhance drafting quality

---

## Disclaimer

This project is for educational purposes only and should not be used as a replacement for professional legal advice.

---



