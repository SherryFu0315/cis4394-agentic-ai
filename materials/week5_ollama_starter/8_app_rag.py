"""
Week 9: the Week 7 RAG agent, wrapped as a chat app you can open on your phone.

    ./venv/bin/python 8_app_rag.py            # http://localhost:7860 on this laptop
    LAN=1   ./venv/bin/python 8_app_rag.py    # same Wi-Fi: open http://<this laptop's IP>:7860 on your phone
    SHARE=1 ./venv/bin/python 8_app_rag.py    # also prints a public *.gradio.live link (72 h)

Nothing about the agent changed. Only the harness did: input() became a text box,
print() became a chat bubble. Requires course_index.json from 7_rag_local.py index.
"""
import os, importlib, gradio as gr, ollama

rag   = importlib.import_module("7_rag_local")          # reuse, don't rewrite
MODEL = os.environ.get("MODEL", "qwen2.5:0.5b")
TOP_K = int(os.environ.get("TOP_K", 3))

def answer(message, history):
    hits = rag.retrieve(message, TOP_K)
    passages = "\n\n".join(f"[{r}] (from {c['source']})\n{c['text']}" for r, (_, c) in enumerate(hits, 1))
    system = ("You answer questions about a university course using only the passages you are given. "
              "If the passages do not answer the question, reply: Not in the course documents.")
    user = (f"Passages:\n\n{passages}\n\nQuestion: {message}\n\n"
            "Answer in one or two sentences, then write the passage number you used in brackets.")
    reply = ollama.chat(model=MODEL, messages=[{"role": "system", "content": system},
                                               {"role": "user", "content": user}]).message.content
    sources = "  ·  ".join(f"[{r}] {c['source']} #{c['i']} ({s:.2f})" for r, (s, c) in enumerate(hits, 1))
    return f"{reply.strip()}\n\n<sub>retrieved: {sources}</sub>"

app = gr.ChatInterface(
    fn=answer,
    title="Ask CIS 4394",
    description=f"A local model ({MODEL}) answering from the course website. Nothing leaves this laptop"
                + (" — except through the share link you just created." if os.environ.get("SHARE") else "."),
    examples=["When is Quiz 3 and what does it cover?",
              "What does Group Assignment 2 require?",
              "Who teaches CIS 4394 in Spring 2027?"],
)

if __name__ == "__main__":
    app.launch(share=bool(os.environ.get("SHARE")),                      # SHARE=1 -> public *.gradio.live link
               server_name="0.0.0.0" if os.environ.get("LAN") else None,    # LAN=1   -> phones on the same Wi-Fi can open it
               server_port=int(os.environ.get("PORT", 7860)))
