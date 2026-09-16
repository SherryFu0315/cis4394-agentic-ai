CIS 4394 Agentic AI · Week 5 · Build a tool-calling agent on a LOCAL model (Ollama)
No API key, no cost. Everything runs on your laptop.

BEFORE YOU START
  1. Ollama is installed and running (open the Ollama app, or run: ollama serve)
  2. You have a model that supports tools. Check with:  ollama show qwen2.5:0.5b
     -> the "Capabilities" list must include "tools"
  3. Python 3 (tested on 3.11)

SETUP (once)
  python -m venv venv
  source venv/bin/activate          (Windows: venv\Scripts\activate)
  pip install -r requirements.txt

THE FILES
  1_agent_raw.py            The whole agent loop in ~60 lines, plain Python + ollama. Start here.
                            python 1_agent_raw.py "What is 4817 * 293?"
  2_pass_k.py               Run the agent k times, report pass^k.
                            python 2_pass_k.py qwen2.5:0.5b 3
  3_agent_langgraph.py      The same agent rebuilt in LangGraph (Week 4 concepts).
                            python 3_agent_langgraph.py
  4_tool_design_ladder.py   Can tool design rescue a small model? Three setups, measured.
                            python 4_tool_design_ladder.py qwen2.5:0.5b 3

USING A DIFFERENT MODEL
  Scripts 2 and 4 take the model name as the first argument.
  For scripts 1 and 3, either edit the MODEL = ... line at the top, or set an environment variable:
    Mac/Linux:   MODEL=llama3.2 python 1_agent_raw.py
    PowerShell:  $env:MODEL="llama3.2"; python 1_agent_raw.py
    cmd.exe:     set MODEL=llama3.2 && python 1_agent_raw.py

Small models make mistakes. Observing and measuring those mistakes is part of the lab, not a bug in your code.
Full instructions: https://sherryfu0315.github.io/cis4394-agentic-ai/week5/local.html
