# CIS 4394 · Agentic AI — Georgia State University (Fall 2026)

**Interactive course site:** https://sherryfu0315.github.io/cis4394-agentic-ai/

Generative AI is evolving into **agentic AI** — systems that reason, plan, adapt, and collaborate in complex environments. This undergraduate course at Georgia State University's J. Mack Robinson College of Business teaches the foundations *and* the practice: from the agent loop and tool use to evaluation, safety, governance, and deployment, ending in an individual capstone agent.

Taught by **Dr. Xinyu Fu** ([faculty profile](https://robinson.gsu.edu/profile/xinyu-fu/) · [personal site](https://sherryfu0315.github.io/) · xfu11 \[at\] gsu \[dot\] edu), Computer Information Systems, Robinson College of Business. The course is offered within [PATH — Pathways for AI Training & Hiring](https://path.mit.edu/), a national initiative led by MIT RAISE and Georgia State University ([about PATH](https://sherryfu0315.github.io/cis4394-agentic-ai/path.html)).

## What's in this repository

Each week of the course ships as an **interactive mini-site** — clickable architecture explorers, step-through agent-loop simulators, live concept checks, autonomy dials, and complete lab instructions — plus downloadable class materials. Content is published week by week as the semester progresses.

| Week | Topic | Site | Highlights |
|---|---|---|---|
| **1** | Introduction to Agentic AI + What Enterprises Actually Use | [week1/](https://sherryfu0315.github.io/cis4394-agentic-ai/week1/) | The agent loop as a step-through simulator · agent vs workflow vs chatbot · an autonomy dial you can turn · the five workflow patterns · the 2026 enterprise agent stack · classify-the-scenario exercises · free toolchain setup |
| **2** | Learning from the Best: Unpacking Coding Agents | [week2/](https://sherryfu0315.github.io/cis4394-agentic-ai/week2/) | Reverse-engineer Codex layer by layer · the same architecture lens on Claude Code · build a Job Search Agent three ways (Google Opal, LangSmith Fleet, or Codex + Python) with four behavior tests including a prompt-injection case, real human-approval gates, and a path-neutral rubric |
| **3** | Prompting & Context Engineering | [week3/](https://sherryfu0315.github.io/cis4394-agentic-ai/week3/) | A clickable annotated prompt · few-shot, chain-of-thought, structured JSON output · an interactive temperature dial · the context-window packing game · context rot · the $1 Chevy Tahoe case study |
| **4** | Reasoning, Planning & the Agent Loop | [week4/](https://sherryfu0315.github.io/cis4394-agentic-ai/week4/) | A step-through agent loop · ReAct, plan-then-execute, reflection and Tree of Thoughts with the papers · the cost of thinking harder · prompting vs fine-tuning shown on visible weights · a minimal LangGraph agent with a max-iteration guard |
| **5** | Tool Use & Function Calling | [week5/](https://sherryfu0315.github.io/cis4394-agentic-ai/week5/) | The function-calling round trip, step by step · schemas as interfaces · errors as observations the model can act on · the auto-run / constrain / human-gate decision · a tool-boundary mapping exercise |
| **6** | MCP & A2A — the interoperability standards | [week6/](https://sherryfu0315.github.io/cis4394-agentic-ai/week6/) | The N×M integration problem, before and after · a clickable MCP architecture · A2A and Agent Cards · which standard when · why a third-party server sits inside your trust boundary |
| **7** | Memory, RAG & Knowledge | [week7/](https://sherryfu0315.github.io/cis4394-agentic-ai/week7/) | Working, episodic, semantic and procedural memory · the RAG pipeline as a step-through · embeddings as geometry · grounding and citations · RAG vs fine-tuning, decided on the evidence |
| **8** | Evaluation & Reliability | [week8/](https://sherryfu0315.github.io/cis4394-agentic-ai/week8/) | Why demos lie · outcome vs trajectory evaluation · pass@k vs pass^k with a calculator you can push · benchmark literacy (SWE-bench, WebArena, τ-bench) · LLM-as-judge and its biases |
| **9** | Multi-Agent Systems | [week9/](https://sherryfu0315.github.io/cis4394-agentic-ai/week9/) | Supervisor, network and hierarchical topologies, clickable · what actually gets shared between agents · the honest case against multi-agent · documented failure modes · split-or-don't decisions |
| **10** | Security, Trust & Governance | [week10/](https://sherryfu0315.github.io/cis4394-agentic-ai/week10/) | The lethal trifecta as three toggles you can flip · indirect prompt injection as an architecture problem · least-privilege tools · NIST AI RMF vs the EU AI Act · an attack-and-patch lab |
| **11** | Agentic Commerce | [week11/](https://sherryfu0315.github.io/cis4394-agentic-ai/week11/) | What changes when the action moves money · the emerging payment protocols (AP2, ACP) · computer-use agents and the humbling benchmarks · the deployment checklist and the gate that must hold |
| 12–14 | Capstone studios, final presentations & course wrap-up | *coming soon* | Published here as the semester reaches them |

Downloadable materials (lecture deck, lab starter kits) live in [`materials/`](materials/).

## Course design principles

- **Real systems, not toy demos.** Week 2 starts by reading the actual Codex repository; labs use production tools (LangGraph, LangSmith Fleet, Google Opal, Codex CLI, GitHub Copilot).
- **Zero cost to students.** Every tool runs on a free tier — no paid API keys, no credit cards.
- **Agents, not workflows.** Full credit requires runtime evidence that different observations produce different action sequences. A fixed pipeline caps the grade.
- **Safety is graded, not preached.** Every build includes truthfulness guardrails, untrusted-data handling (prompt-injection tests), a named stop condition, and a human-approval gate.
- **Claims are dated and sourced.** Agentic AI moves fast; every statistic on these pages carries its source and an "approximate" flag where appropriate.

## Tech

The sites are dependency-free static HTML/CSS/JS (no build step, no framework) — view source is part of the pedagogy. Design system: GSU palette, Fraunces/Inter/JetBrains Mono.

## License & reuse

© 2026 Xinyu Fu. Course materials are shared for educational use; contact the instructor for reuse or adaptation. Adapted open items (Microsoft *AI Agents for Beginners* — MIT; Hugging Face Agents Course — Apache-2.0; LangChain Academy — MIT) are used with attribution. Product names and logos (Google Opal, LangChain, OpenAI, GitHub) are trademarks of their respective owners, used for identification. Cited statistics are summarized in original words with sources named — verify against primary sources before quoting.
