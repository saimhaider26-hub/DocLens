import os
import requests
from typing import TypedDict, Literal
from langgraph.graph import StateGraph, END
from src.qa import generate_cited_answer
from src.sqlAgent import run_sql_agent

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

class AgentState(TypedDict):
    question: str
    route: str
    answer: str

def classify_question(question: str) -> str:
    prompt = f"""Analyze the following question and classify it into exactly one of these two categories:
    1. 'data': If the question asks about business records, numbers, invoices, customers, or transactions.
    2. 'document': If the question asks about company policies, summaries, textual information, or general knowledge.
    
    Return ONLY the word 'data' or 'document'. Nothing else.
    
    Question: {question}"""
    
    payload = {
        "model": "llama3.1",
        "prompt": prompt,
        "stream": False,
        "temperature": 0.0
    }
    
    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()["response"].strip().lower()
        if "data" in result:
            return "data"
        return "document"
    except:
        return "document"

def router_node(state: AgentState) -> AgentState:
    route = classify_question(state["question"])
    return {"question": state["question"], "route": route, "answer": ""}

def rag_node(state: AgentState) -> AgentState:
    answer = generate_cited_answer(state["question"])
    return {"question": state["question"], "route": state["route"], "answer": answer}

def sql_node(state: AgentState) -> AgentState:
    result = run_sql_agent(state["question"])
    answer = f"SQL Query used: {result.get('query')}\nResults: {result.get('results')}"
    return {"question": state["question"], "route": state["route"], "answer": answer}

def determine_next_step(state: AgentState) -> Literal["rag_node", "sql_node"]:
    if state["route"] == "data":
        return "sql_node"
    return "rag_node"

workflow = StateGraph(AgentState)

workflow.add_node("router_node", router_node)
workflow.add_node("rag_node", rag_node)
workflow.add_node("sql_node", sql_node)

workflow.set_entry_point("router_node")

workflow.add_conditional_edges(
    "router_node",
    determine_next_step,
    {
        "rag_node": "rag_node",
        "sql_node": "sql_node"
    }
)

workflow.add_edge("rag_node", END)
workflow.add_edge("sql_node", END)

app = workflow.compile()

def run_router(question: str):
    initial_state = {"question": question, "route": "", "answer": ""}
    return app.invoke(initial_state)

if __name__ == "__main__":
    print("Testing SQL Route:")
    print(run_router("How many invoices are PAID?"))
    print("\nTesting RAG Route:")
    print(run_router("What is SMART IS?"))