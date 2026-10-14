"""
Week 9: two agents behind one chat window - the smallest honest multi-agent system.

    ./venv/bin/python 8_app_router.py            # http://localhost:7862

A SUPERVISOR decides which specialist gets the message:
    course agent  (8_app_rag.py)     - can read the course index, cannot touch orders
    order agent   (8_app_orders.py)  - can look up / refund orders, cannot read the course
Each specialist sees only its own tools and its own context. That isolation is the
real reason production apps split into agents - not because two models are smarter.
The router here is a RULE, not a model: deterministic, testable, and it is the first
thing you would measure with pass^k if you replaced it with a model.
"""
import os, re, importlib, gradio as gr

course = importlib.import_module("8_app_rag")
orders = importlib.import_module("8_app_orders")
MODEL  = os.environ.get("MODEL", "qwen2.5:0.5b")

def route(message, state):
    """Supervisor policy. Returns 'orders' or 'course'."""
    if state and state.get("pending"):                 # a refund is waiting for yes/no: stay with the order agent
        return "orders"
    if re.search(r"\bORD-\d+\b", message, re.I) or re.search(r"\b(refund|order|return|shipping|ship)\b", message, re.I):
        return "orders"
    return "course"

def respond(message, history, state):
    who = route(message, state)
    if who == "orders":
        reply, state = orders.respond(message, history, state)
    else:
        reply = course.answer(message, history)
    return f"<sub>supervisor → {who} agent</sub>\n\n{reply}", state

with gr.Blocks(title="Front Desk") as app:
    gr.Markdown(f"## Front desk — one window, two agents ({MODEL})\n"
                "Try: *When is Quiz 3?* · *Where is my order ORD-004411?* · *Refund order ORD-004412, it arrived damaged* · *What does GA2 require?*")
    state = gr.State()
    gr.ChatInterface(fn=respond, additional_inputs=[state], additional_outputs=[state])

if __name__ == "__main__":
    app.launch(share=bool(os.environ.get("SHARE")),
               server_name="0.0.0.0" if os.environ.get("LAN") else None,
               server_port=int(os.environ.get("PORT", 7862)))
