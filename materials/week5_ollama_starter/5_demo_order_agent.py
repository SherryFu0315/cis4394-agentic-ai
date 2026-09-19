"""
Week 5 live demo: a small customer-service agent on a LOCAL model.
Two tools, two very different risk levels:
    lookup_order   - read-only  -> runs automatically
    issue_refund   - spends money -> STOPS and asks a human first

Run:  python 5_demo_order_agent.py
      python 5_demo_order_agent.py "Refund order ORD-004412, it arrived damaged"
"""
import os, sys, ollama

MODEL = os.environ.get("MODEL", "qwen2.5:0.5b")
MAX_STEPS = 6
ORDERS = {
    "ORD-004411": {"status": "shipped",    "items": 2, "total": 84.20},
    "ORD-004412": {"status": "processing", "items": 1, "total": 19.99},
}

def lookup_order(order_id: str) -> str:
    """Look up the status, item count and total of one customer order.
    Use this whenever the customer mentions an order number or asks where an
    order is. Never answer questions about an order from memory.

    Args:
        order_id: the order number, like 'ORD-004411'
    """
    o = ORDERS.get(order_id.upper())
    if not o:
        return f"OrderNotFound: no order {order_id}. Ask the customer to confirm the number."
    return f"status={o['status']}, items={o['items']}, total=${o['total']:.2f}"

def issue_refund(order_id: str, amount_usd: float, reason: str) -> str:
    """Refund money to the customer for one order. Only use when the customer asks for a refund.

    Args:
        order_id: the order number, like 'ORD-004411'
        amount_usd: how much money to refund, in dollars
        reason: short reason for the refund, e.g. 'damaged'
    """
    return f"REFUNDED ${float(amount_usd):.2f} on {order_id} ({reason})"

TOOLS = {"lookup_order": lookup_order, "issue_refund": issue_refund}
NEEDS_APPROVAL = {"issue_refund"}          # the human gate: money and anything irreversible

def approve(name, args) -> bool:
    print("\n  ┌─ APPROVAL NEEDED ─────────────────────────────")
    print(f"  │ {'action':<11}: {name}")
    for k, v in args.items():
        print(f"  │ {k:<11}: {v}")
    print("  └───────────────────────────────────────────────")
    if os.environ.get("AUTO_APPROVE"):     # for scripted testing only
        print("  (auto-approved for testing)")
        return os.environ["AUTO_APPROVE"] == "y"
    return input("  Approve? [y/N] ").strip().lower() == "y"

def run(goal: str):
    messages = [
        {"role": "system", "content":
            "You are a customer-service assistant for an online store.\n"
            "- If the message contains an order number like ORD-004411, call lookup_order for it.\n"
            "- Call issue_refund ONLY if the customer explicitly asks for a refund or their money back.\n"
            "- If the message contains no order number, do NOT call any tool. Answer in one or two sentences."},
        {"role": "user", "content": goal},
    ]
    for step in range(1, MAX_STEPS + 1):
        msg = ollama.chat(model=MODEL, messages=messages, tools=list(TOOLS.values())).message
        messages.append(msg)
        if not msg.tool_calls:
            print(f"\n[step {step}] FINAL ANSWER:\n{msg.content}")
            return msg.content
        for call in msg.tool_calls:
            name, args = call.function.name, dict(call.function.arguments)
            print(f"\n[step {step}] model requests -> {name}({args})")
            if name in NEEDS_APPROVAL and not approve(name, args):
                result = "DENIED by the human reviewer. Do not retry; tell the customer a person will follow up."
            else:
                try:
                    result = TOOLS[name](**args) if name in TOOLS else f"ERROR: unknown tool {name}"
                except Exception as e:
                    result = f"ERROR calling {name}: {e}. Check the argument types."
            print(f"          result <- {result}")
            messages.append({"role": "tool", "content": result, "tool_name": name})
    print(f"\nSTOPPED at the {MAX_STEPS}-step cap.")

if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or "Where is my order ORD-004411?")
