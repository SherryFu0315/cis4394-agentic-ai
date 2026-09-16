"""
Same agent, rebuilt in LangGraph on the local model. Only the model line changed from Week 4's Gemini version.
Run:  pip install -r requirements.txt   then   python 3_agent_langgraph.py
"""
import os
from typing import Annotated
from typing_extensions import TypedDict
from langchain_core.tools import tool
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

MODEL = os.environ.get("MODEL", "qwen2.5:0.5b")   # or edit this line
MAX_STEPS = 8

@tool
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression like '4817 * 293' and return the exact result."""
    if not set(expression) <= set("0123456789+-*/(). "):
        return "ERROR: only numbers and + - * / ( ) are allowed"
    return str(round(eval(expression), 2))

@tool
def get_exchange_rate(base: str, target: str) -> str:
    """Look up the exchange rate between two 3-letter currency codes, e.g. base='EUR', target='USD'."""
    rates = {("EUR", "USD"): 1.08, ("USD", "EUR"): 0.93, ("GBP", "USD"): 1.27}
    r = rates.get((base.upper(), target.upper()))
    return str(r) if r else f"ERROR: no rate for {base}->{target}"

tools = [calculator, get_exchange_rate]
llm = ChatOllama(model=MODEL, temperature=0).bind_tools(tools)   # <-- the only line that differs from Gemini

class State(TypedDict):
    messages: Annotated[list, add_messages]
    steps: int

def call_model(state: State):
    return {"messages": [llm.invoke(state["messages"])], "steps": state["steps"] + 1}

def guarded(state: State):
    if state["steps"] >= MAX_STEPS:          # the max-iteration guard: harness decides, not the model
        return END
    return tools_condition(state)

g = StateGraph(State)
g.add_node("model", call_model)
g.add_node("tools", ToolNode(tools))
g.add_edge(START, "model")
g.add_conditional_edges("model", guarded)
g.add_edge("tools", "model")                 # <-- the loop
agent = g.compile()

if __name__ == "__main__":
    out = agent.invoke({"steps": 0, "messages": [
        ("system", "You are a finance assistant. Use tools for every number; never do arithmetic in your head."),
        ("user", "An invoice is 4817 units at 293 EUR each, plus 18% tax. What is the total in USD?")]})
    for m in out["messages"]:
        m.pretty_print()
