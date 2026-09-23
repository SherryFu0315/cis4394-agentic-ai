"""
Week 5 starter: a tool-calling agent on a LOCAL model (Ollama). No API key, no cost.
Run:  pip install ollama   then   python 1_agent_raw.py "What is 4817 * 293?"
"""
import os, sys
import ollama

MODEL = os.environ.get("MODEL", "qwen2.5:0.5b")   # or edit this line: any model whose `ollama show` lists: tools
MAX_STEPS = 8                                   # Week 4: the harness, not the model, decides when to stop

# ---------- TOOLS: plain Python functions. The docstring IS the tool description. ----------
def calculator(expression: str) -> str:
    """Evaluate an arithmetic expression and return the exact result.

    Args:
        expression: A math expression using numbers and + - * / ( ) . e.g. '4817 * 293'
    """
    if not set(expression) <= set("0123456789+-*/(). "):
        return "ERROR: only numbers and + - * / ( ) are allowed"
    try:
        return str(round(eval(expression), 2))
    except Exception as e:
        return f"ERROR: {e}"

def get_exchange_rate(base: str, target: str) -> str:
    """Look up the exchange rate between two currencies.

    Args:
        base: 3-letter currency code to convert FROM, e.g. 'EUR'
        target: 3-letter currency code to convert TO, e.g. 'USD'
    """
    rates = {("EUR", "USD"): 1.08, ("USD", "EUR"): 0.93, ("GBP", "USD"): 1.27}  # stub data for class
    rate = rates.get((base.upper(), target.upper()))
    return str(rate) if rate else f"ERROR: no rate for {base}->{target}. Use 3-letter codes like EUR, USD."

TOOLS = {"calculator": calculator, "get_exchange_rate": get_exchange_rate}

# ---------- THE LOOP ----------
def run(goal: str):
    messages = [
        {"role": "system", "content": "You are a finance assistant. Use tools for every number; never do arithmetic in your head. When you have the final answer, reply without calling a tool."},
        {"role": "user", "content": goal},
    ]
    for step in range(1, MAX_STEPS + 1):
        resp = ollama.chat(model=MODEL, messages=messages, tools=list(TOOLS.values()))
        msg = resp.message
        messages.append(msg)

        if not msg.tool_calls:                      # model chose to FINISH
            print(f"\n[step {step}] FINAL ANSWER:\n{msg.content}")
            return msg.content

        for call in msg.tool_calls:                 # model chose to ACT
            name, args = call.function.name, call.function.arguments
            print(f"[step {step}] model requests -> {name}({args})")
            fn = TOOLS.get(name)
            try:                                     # Week 5: an error is an OBSERVATION, not a crash
                result = fn(**args) if fn else f"ERROR: unknown tool {name}"
            except Exception as e:
                result = f"ERROR calling {name}: {e}. Check the argument types and try again."
            print(f"          harness ran it   <- {result}")
            messages.append({"role": "tool", "content": result, "tool_name": name})

    print(f"\nSTOPPED: hit MAX_STEPS={MAX_STEPS} without a final answer")

if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or "An invoice is 4817 units at 293 EUR each, plus 18% tax. What is the total in USD?")
