from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from legal_assistant.state import LegalState
from legal_assistant.nodes import (
    
    router_node,
    retrieval_node,
    
    tool_node,
    answer_node,
    eval_node,
    save_node
)


def route_decision(state):
    return state["route"]


def eval_decision(state):
    if state["faithfulness"] < 0.7 and state["eval_retries"] < 2:
        return "answer"
    return "save"


def build_graph(llm, collection, embedder):
    g = StateGraph(LegalState)

    
    g.add_node("router", router_node)
    g.add_node("retrieve", lambda state: retrieval_node(state, collection, embedder))
    g.add_node("answer",   lambda state: answer_node(state, llm))
    g.add_node("eval",     lambda state: eval_node(state, llm))
    g.add_node("tool", tool_node)
    
    g.add_node("save", save_node)

    g.set_entry_point("router")


    g.add_conditional_edges("router", route_decision, {
        "retrieve": "retrieve",
        "tool": "tool"
    })

    g.add_edge("retrieve", "answer")
    g.add_edge("tool", "answer")
    

    g.add_edge("answer", "eval")

    g.add_conditional_edges("eval", eval_decision, {
        "answer": "answer",
        "save": "save"
    })

    g.add_edge("save", END)

    return g.compile(checkpointer=MemorySaver())