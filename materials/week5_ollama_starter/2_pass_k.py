"""
Run the Week 5 agent k times on one model and report pass^k (Week 8 preview).
Usage:  python 2_pass_k.py llama3.2 3
"""
import os, re, sys, io, contextlib, importlib.util
model, k = sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3
os.environ["MODEL"] = model
spec = importlib.util.spec_from_file_location("agent", os.path.join(os.path.dirname(__file__), "1_agent_raw.py"))
agent = importlib.util.module_from_spec(spec); spec.loader.exec_module(agent)

def is_correct(answer: str, target: float) -> bool:
    """True only if some number in the answer equals the target (within 1 cent). No substring tricks."""
    for tok in re.findall(r"\d[\d,]*(?:\.\d+)?", answer):
        try:
            if abs(float(tok.replace(",", "")) - target) < 0.01:
                return True
        except ValueError:
            pass
    return False

EXPECTED = 1798663.95   # 4817 * 293 * 1.18 * 1.08
passed = 0
for i in range(k):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        answer = agent.run("An invoice is 4817 units at 293 EUR each, plus 18% tax. What is the total in USD?") or ""
    tools_used = re.findall(r"model requests -> (\w+)", buf.getvalue())
    ok = is_correct(answer, EXPECTED)
    passed += ok
    print(f"run {i+1}: {'PASS' if ok else 'FAIL'}  tools called: {tools_used or 'NONE'}")
print(f"\n{model}: {passed}/{k} correct · pass^{k} = {'YES' if passed == k else 'NO'}")
