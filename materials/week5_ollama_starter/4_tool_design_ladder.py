"""
Week 5 lab: can TOOL DESIGN rescue a tiny model?  Same question, three setups, k runs each.
Usage:  python 4_tool_design_ladder.py qwen2.5:0.5b 3
Measured on qwen2.5:0.5b, Sept 2026, pooled over several runs (yours will vary run to run):
  A single step: 16/16 right · B multi-step, fine tools: 0/16 · C one coarse tool: tool right 12/15, final answer right only 6/23
"""
import io, os, re, sys, contextlib, importlib.util
model = sys.argv[1] if len(sys.argv) > 1 else "qwen2.5:0.5b"
k = int(sys.argv[2]) if len(sys.argv) > 2 else 3
os.environ["MODEL"] = model
spec = importlib.util.spec_from_file_location("agent", os.path.join(os.path.dirname(__file__), "1_agent_raw.py"))
a = importlib.util.module_from_spec(spec); spec.loader.exec_module(a)
FINE = dict(a.TOOLS)

def invoice_total(units: int, unit_price: float, tax_rate_percent: float, from_currency: str, to_currency: str) -> str:
    """Compute an invoice total including tax, converted to another currency. Returns the exact final amount.

    Args:
        units: number of units, e.g. 4817
        unit_price: price per unit in from_currency, e.g. 293
        tax_rate_percent: tax as a percent, e.g. 18 for 18%
        from_currency: 3-letter code of the price currency, e.g. 'EUR'
        to_currency: 3-letter code to convert to, e.g. 'USD'
    """
    r = {("EUR", "USD"): 1.08, ("USD", "EUR"): 0.93}.get((from_currency.upper(), to_currency.upper()))
    if r is None:
        return f"ERROR: no rate {from_currency}->{to_currency}"
    return str(round(float(units) * float(unit_price) * (1 + float(tax_rate_percent) / 100) * r, 2))

def is_correct(answer: str, target: float) -> bool:
    """True only if some number in the answer equals the target (within 1 cent). No substring tricks."""
    for tok in re.findall(r"\d[\d,]*(?:\.\d+)?", answer):
        try:
            if abs(float(tok.replace(",", "")) - target) < 0.01:
                return True
        except ValueError:
            pass
    return False

INVOICE = "An invoice is 4817 units at 293 EUR each, plus 18% tax. What is the total in USD?"
SETUPS = [
    ("A. single step, fine-grained tools", FINE, "What is 4817 * 293?", 1411381.0),
    ("B. multi-step, fine-grained tools ", FINE, INVOICE, 1798663.95),
    ("C. multi-step, ONE coarse tool    ", {"invoice_total": invoice_total}, INVOICE, 1798663.95),
]
for label, tools, question, expected in SETUPS:
    a.TOOLS.clear(); a.TOOLS.update(tools)
    tool_ok = final_ok = 0
    for _ in range(k):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            ans = a.run(question) or ""
        tool_ok += any(is_correct(line.split("<-", 1)[1], expected) for line in buf.getvalue().splitlines() if "<-" in line)
        final_ok += is_correct(ans, expected)
    print(f"{label}: a tool produced the right number {tool_ok}/{k} · final answer right {final_ok}/{k}")
print("\nDiscuss 1: in C the tool usually gets the number right, but does the final answer? Where should that number come from?")
print("Discuss 2: C moved the plan out of the model and into your code. Is it still an agent, or a workflow? (Week 1)")
