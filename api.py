"""
api.py — FastAPI wrapper for Legal Assistant Agent

Run:
    uvicorn api:app --reload --port 8000
"""

from datetime import datetime
from typing import Optional, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Import your agent interface
from agent import chat


app = FastAPI(
    title=" Legal Assistant API",
    version="1.0.0",
    description="Agentic Legal AI powered by LangGraph"
)



class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)
    thread_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    response: str
    intent: str
    eval_passed: bool
    sources: List[str]
    thread_id: str
    timestamp: str

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "Legal Assistant",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    try:
        result = chat(
            user_message=request.message,
            thread_id=request.thread_id
        )

        return ChatResponse(
            response=result.get("response", ""),
            intent=result.get("intent", "unknown"),
            eval_passed=result.get("eval_passed", True),
            sources=result.get("sources", []),
            thread_id=result.get("thread_id", request.thread_id),
            timestamp=datetime.now().isoformat()
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
def root():
    return {
        "message": "LegalAI API is running 🚀",
        "docs": "/docs"
    }
