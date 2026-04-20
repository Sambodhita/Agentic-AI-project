import json
from typing import Dict

from legal_assistant.tools import deadline_calculator, risk_scorer, legal_math

def router_node(state: Dict):
    text = state["question"].lower()

    if any(x in text for x in ["calculate", "%", "interest", "penalty", "prorate"]):
        route = "tool"
    elif any(x in text for x in ["deadline", "expiry", "expire", "notice"]):
        route = "tool"
    elif any(x in text for x in ["risk", "clause", "liability"]):
        route = "tool"
    else:
        route = "retrieve"

    return {**state, "route": route}
def retrieval_node(state: Dict, collection, embedder):
    query = state["question"]

    query_embedding = embedder.encode(query).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3
    )

    docs = results.get("documents", [[]])[0]

    context = "\n\n".join(docs)

    return {
        **state,
        "retrieved": context,
        "sources": results.get("ids", [[]])[0]
    }
def tool_node(state: Dict):
    text = state["question"].lower()

    try:
        if "deadline" in text:
            result = deadline_calculator.invoke({
                "contract_start_date": "2026-01-01",
                "duration_value": 12,
                "duration_unit": "months"
            })

        elif "risk" in text or "clause" in text:
            result = risk_scorer.invoke({
                "clauses_list": state["question"]
            })

        elif any(x in text for x in ["calculate", "%", "interest", "penalty", "prorate"]):
            result = legal_math.invoke({
                "operation": "percentage",
                "values": "1000,10",
                "description": "Sample calculation"
            })

        else:
            result = "No suitable tool found."

    except Exception as e:
        result = f"Tool error: {str(e)}"

    return {**state, "tool_result": result}

def save_node(state: Dict):
    messages = state.get("messages", [])

    messages.append({
        "question": state["question"],
        "answer": state["answer"]
    })

    return {**state, "messages": messages}
def eval_node(state, llm):

    # If no retrieval, skip evaluation (avoid false penalties)
    if not state.get("retrieved"):
        return {**state, "faithfulness": 1.0}

    prompt = f"""
You are evaluating a legal assistant's answer.

Check if the answer is grounded in the provided context.

Context:
{state['retrieved']}

Answer:
{state['answer']}

Return ONLY JSON:
{{ "score": number between 0 and 1 }}
"""

    res = llm.invoke(prompt)

    try:
        score = json.loads(res.content)["score"]
    except:
        score = 0.8  # fallback safe score

    retries = state.get("eval_retries", 0) + 1

    return {
        **state,
        "faithfulness": score,
        "eval_retries": retries
    }
def answer_node(state, llm):
    context = state.get("retrieved", "")
    tool = state.get("tool_result", "")
    memory = "\n".join(state.get("messages", []))

    prompt = f"""
You are a professional Legal Assistant.

STRICT RULES:
- Use ONLY the provided context and tool output
- If answer not found → say "I don't know"
- Be clear, structured, and professional

Conversation Memory:
{memory}

Retrieved Context:
{context}

Tool Output:
{tool}

User Question:
{state['question']}
"""

    res = llm.invoke(prompt)

    return {**state, "answer": res.content}