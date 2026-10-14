"""
Week 9: the Week 5 order agent (lookup + refund) as a chat app, with the human gate
turned into a conversation turn.

    ./venv/bin/python 8_app_orders.py            # http://localhost:7861
    LAN=1   ./venv/bin/python 8_app_orders.py    # same Wi-Fi: open http://<this laptop's IP>:7861 on your phone
    SHARE=1 ./venv/bin/python 8_app_orders.py    # public link -> now ask: who can approve a refund?

The terminal version stopped at input("Approve? [y/N]"). A web app cannot block on
input(), so the gate becomes STATE: the app remembers the pending refund and waits
for the next message to say yes or no.
"""
import os, importlib, gradio as gr, ollama

base  = importlib.import_module("5_demo_order_agent")    # reuse the tools + system prompt rules
MODEL = os.environ.get("MODEL", "qwen2.5:0.5b")
MAX_STEPS = 6
TOOLS, NEEDS_APPROVAL = base.TOOLS, base.NEEDS_APPROVAL

SYSTEM = ("You are a customer-service assistant for an online store.\n"
          "- If the message contains an order number like ORD-004411, call lookup_order for it.\n"
          "- Call issue_refund ONLY if the customer explicitly asks for a refund or their money back.\n"
          "- If the message contains no order number, do NOT call any tool. Answer in one or two sentences.")

def run_loop(messages, log):
    """Advance the agent until it answers, or until it proposes a gated action (returns it as pending)."""
    for _ in range(MAX_STEPS):
        msg = ollama.chat(model=MODEL, messages=messages, tools=list(TOOLS.values())).message
        messages.append(msg)
        if not msg.tool_calls:
            return msg.content, None
        for call in msg.tool_calls:
            name, args = call.function.name, dict(call.function.arguments)
            log.append(f"→ {name}({args})")
            if name in NEEDS_APPROVAL:
                return None, (name, args)                      # stop: a human must decide
            try:
                result = TOOLS[name](**args) if name in TOOLS else f"ERROR: unknown tool {name}"
            except Exception as e:
                result = f"ERROR calling {name}: {e}"
            log.append(f"← {result}")
            messages.append({"role": "tool", "content": result, "tool_name": name})
    return "Stopped at the step cap.", None

def respond(message, history, state):
    state = state or {"messages": [{"role": "system", "content": SYSTEM}], "pending": None}
    log = []
    if state["pending"]:                                       # the human is answering the gate
        name, args = state["pending"]; state["pending"] = None
        if message.strip().lower() in ("y", "yes", "approve"):
            result = TOOLS[name](**args); log.append(f"✅ approved → {result}")
        else:
            result = "DENIED by the human reviewer. Do not retry; tell the customer a person will follow up."
            log.append("⛔ denied")
        state["messages"].append({"role": "tool", "content": result, "tool_name": name})
    else:
        state["messages"].append({"role": "user", "content": message})
    final, pending = run_loop(state["messages"], log)
    trace = "\n".join(f"<sub>{l}</sub>" for l in log)
    if pending:
        state["pending"] = pending
        name, args = pending
        box = "\n".join(f"**{k}**: {v}" for k, v in args.items())
        return f"⚠️ **APPROVAL NEEDED** — `{name}`\n\n{box}\n\nReply **yes** to approve or **no** to deny.\n\n{trace}", state
    return f"{(final or '').strip()}\n\n{trace}", state

with gr.Blocks(title="Order Desk") as app:
    gr.Markdown(f"## Order desk — a local agent with a human gate ({MODEL})\nTry: *Where is my order ORD-004411?* · *Refund order ORD-004412, it arrived damaged* · *Do you ship to Canada?*")
    state = gr.State()
    gr.ChatInterface(fn=respond, additional_inputs=[state], additional_outputs=[state])

if __name__ == "__main__":
    app.launch(share=bool(os.environ.get("SHARE")),                      # SHARE=1 -> public *.gradio.live link
               server_name="0.0.0.0" if os.environ.get("LAN") else None,    # LAN=1   -> phones on the same Wi-Fi can open it
               server_port=int(os.environ.get("PORT", 7861)))
