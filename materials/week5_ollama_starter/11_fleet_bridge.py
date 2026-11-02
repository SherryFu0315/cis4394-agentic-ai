"""
Milestone II helper: give a LangSmith Fleet agent a public, no-login link.

Fleet can share an agent with named LangSmith accounts or a workspace, but it has no
"anyone with the link" option. Every Fleet agent does, however, come with a REST
endpoint. This file is a small Gradio chat page that forwards each message to that
endpoint with YOUR key, so classmates only ever see the page.

    1. In Fleet open your agent -> Advanced settings -> Developer -> View code snippets.
       Copy the api_url (https://....us.langgraph.app) and the agent_id.
    2. Create a Personal Access Token: smith.langchain.com -> Settings -> API keys
       (a PAT tied to the agent's owner; any other key gets 404).
    3. In the terminal you will run from (never in the file, never in the repo):
       Mac/Linux:   export FLEET_API_URL=https://....us.langgraph.app FLEET_AGENT_ID=... LANGSMITH_API_KEY=lsv2_pt_...
       PowerShell:  $env:FLEET_API_URL="https://....us.langgraph.app"; $env:FLEET_AGENT_ID="..."; $env:LANGSMITH_API_KEY="lsv2_pt_..."
    4.           python 11_fleet_bridge.py            # http://localhost:7862 (test it first)
       SHARE=1   python 11_fleet_bridge.py            # public *.gradio.live link, valid 7 days
       LAN=1     python 11_fleet_bridge.py            # same Wi-Fi only

Each browser session gets its own Fleet thread, so the agent keeps the conversation
and every run still lands in your LangSmith traces. Anyone with the link spends YOUR
Fleet allowance (7 LSUs/month on the free plan): keep a cap on turns, connect nothing
real, and stop the script when class is over.

Endpoint reference: https://docs.langchain.com/langsmith/fleet/code
"""
import json, os, urllib.request, urllib.error, gradio as gr

API_URL   = os.environ.get("FLEET_API_URL", "").rstrip("/")
AGENT_ID  = os.environ.get("FLEET_AGENT_ID", "")
API_KEY   = os.environ.get("LANGSMITH_API_KEY") or os.environ.get("LANGGRAPH_API_KEY", "")
MAX_TURNS = int(os.environ.get("MAX_TURNS", 20))      # per browser session; protects your allowance
TIMEOUT   = int(os.environ.get("TIMEOUT", 180))       # seconds to wait for one Fleet run

if not (API_URL and AGENT_ID and API_KEY):
    raise SystemExit("Set FLEET_API_URL, FLEET_AGENT_ID and LANGSMITH_API_KEY first (see the top of this file).")
if not API_URL.startswith("http"):
    API_URL = "https://" + API_URL

HEADERS = {"Content-Type": "application/json",
           "X-Api-Key": API_KEY,
           "X-Auth-Scheme": "langsmith-api-key"}

def fleet(path, body):
    """POST json to the agent's endpoint and return the parsed reply."""
    req = urllib.request.Request(API_URL + path, data=json.dumps(body).encode(), headers=HEADERS, method="POST")
    with urllib.request.urlopen(req, timeout=TIMEOUT) as r:
        return json.loads(r.read().decode() or "{}")

def text_of(content):
    """Fleet messages carry either a string or a list of content blocks."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type", "text") == "text")
    return str(content)

def last_ai_message(result):
    msgs = result.get("messages", []) if isinstance(result, dict) else []
    for m in reversed(msgs):
        if isinstance(m, dict) and (m.get("type") in ("ai", "assistant") or m.get("role") == "assistant"):
            t = text_of(m.get("content", "")).strip()
            if t:
                return t
    return "(no text in the agent's reply)\n```json\n" + json.dumps(result, indent=1)[:1500] + "\n```"

def respond(message, history, state):
    state = state or {"thread_id": None, "turns": 0}
    if state["turns"] >= MAX_TURNS:
        return f"This session reached its {MAX_TURNS}-message cap. Refresh the page to start a new one.", state
    try:
        if not state["thread_id"]:
            state["thread_id"] = fleet("/threads", {})["thread_id"]
        state["turns"] += 1
        result = fleet(f"/threads/{state['thread_id']}/runs/wait",
                       {"assistant_id": AGENT_ID, "input": {"messages": [{"role": "user", "content": message}]}})
        return last_ai_message(result), state
    except urllib.error.HTTPError as e:
        detail = e.read().decode(errors="replace")[:300]
        hint = {401: "key rejected: is it a PAT from the agent owner's account?",
                404: "404: wrong agent_id, wrong api_url, or a key that is not the owner's",
                429: "rate or spend limit reached in Fleet"}.get(e.code, "")
        return f"Fleet returned HTTP {e.code}. {hint}\n\n`{detail}`", state
    except Exception as e:                                    # network, timeout, bad JSON
        return f"Could not reach the agent: {type(e).__name__}: {e}", state

TITLE = os.environ.get("TITLE", "My Fleet agent")
with gr.Blocks(title=TITLE) as app:
    gr.Markdown(f"## {TITLE}\nA LangSmith Fleet agent behind a public page. "
                f"Nothing real is connected; this page is open for a class exercise and will be closed afterwards.")
    state = gr.State()
    gr.ChatInterface(fn=respond, additional_inputs=[state], additional_outputs=[state])

def phone_url(port):
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)); ip = s.getsockname()[0]
    except OSError:
        ip = "127.0.0.1"
    finally:
        s.close()
    return f"http://{ip}:{port}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 7862))
    if os.environ.get("LAN"):
        print(f"\nOn a phone on the same Wi-Fi, open:  {phone_url(port)}\n", flush=True)
    app.launch(share=bool(os.environ.get("SHARE")),
               server_name="0.0.0.0" if os.environ.get("LAN") else None,
               server_port=port)
