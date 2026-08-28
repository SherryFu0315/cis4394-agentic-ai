# CIS 4394 · Agentic AI — Georgia State University (Fall 2026)

**Interactive course site:** https://sherryfu0315.github.io/cis4394-agentic-ai/

Generative AI is evolving into **agentic AI** — systems that reason, plan, adapt, and collaborate in complex environments. This undergraduate course at Georgia State University's J. Mack Robinson College of Business teaches the foundations *and* the practice: from the agent loop and tool use to evaluation, safety, governance, and deployment, ending in an individual capstone agent.

Taught by **Dr. Xinyu Fu** ([xfu11@gsu.edu](mailto:xfu11@gsu.edu)), Computer Information Systems, Robinson College of Business.

## What's in this repository

Each week of the course ships as an **interactive mini-site** — clickable architecture explorers, step-through agent-loop simulators, live concept checks, autonomy dials, and complete lab instructions — plus downloadable class materials. Content is published week by week as the semester progresses.

| Week | Topic | Site | Highlights |
|---|---|---|---|
| **1** | Introduction to Agentic AI + What Enterprises Actually Use | [week1/](https://sherryfu0315.github.io/cis4394-agentic-ai/week1/) | The agent loop as a step-through simulator · agent vs workflow vs chatbot · an autonomy dial you can turn · the five workflow patterns · the 2026 enterprise agent stack · classify-the-scenario exercises · free toolchain setup |
| **2** | Learning from the Best: Unpacking Coding Agents | [week2/](https://sherryfu0315.github.io/cis4394-agentic-ai/week2/) | Reverse-engineer Codex layer by layer · the same architecture lens on Claude Code · build a Job Search Agent three ways (Google Opal, LangSmith Fleet, or Codex + Python) with four behavior tests including a prompt-injection case, real human-approval gates, and a path-neutral rubric |
| 3–14 | Prompting & context engineering · reasoning & planning with LangGraph · tool use · MCP & A2A · memory & RAG · evaluation & reliability · multi-agent systems · security & governance · deployment & agentic commerce · capstone studios | *coming soon* | Published here as the semester progresses |

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
