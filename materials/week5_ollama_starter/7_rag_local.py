"""
Week 7 live demo: RAG on a LOCAL model, with no vector database to install.

The model does not get smarter. It gets a better desk.
Same 0.5B brain, but now the right page is open in front of it.

    ./venv/bin/python 7_rag_local.py index                # embed corpus/ -> course_index.json
    ./venv/bin/python 7_rag_local.py index --dry          # just chunk, show stats, embed nothing
    ./venv/bin/python 7_rag_local.py search "quiz 3"      # retrieval only - no generation
    ./venv/bin/python 7_rag_local.py ask "When is Quiz 3 and what does it cover?"
    ./venv/bin/python 7_rag_local.py ask --no-rag "..."   # same question, closed book
    ./venv/bin/python 7_rag_local.py ask --runs=5 "..."   # repeat generation 5x: how stable is it?
    MODEL=llama3.2 ./venv/bin/python 7_rag_local.py ask "..."   # a bigger reader (2 GB)

Corpus = the course website as plain text (corpus/*.txt), so every answer can be
checked against a page the students have already read.
"""
import os, sys, json, glob, math, time, ollama

MODEL       = os.environ.get("MODEL", "qwen2.5:0.5b")
EMBED_MODEL = os.environ.get("EMBED_MODEL", "nomic-embed-text")
CORPUS_DIR  = "corpus"
INDEX_FILE  = os.environ.get("INDEX_FILE", "course_index.json")
CHUNK_CHARS = int(os.environ.get("CHUNK_CHARS", 700))   # ~175 tokens. Small on purpose: the 0.5B model has a small desk.
TOP_K       = int(os.environ.get("TOP_K", 3))
# nomic-embed-text is trained with task prefixes; retrieval is noticeably worse without them.
DOC_PREFIX   = "search_document: " if EMBED_MODEL.startswith("nomic") else ""
QUERY_PREFIX = "search_query: "    if EMBED_MODEL.startswith("nomic") else ""

# ------------------------------------------------------------------ chunking
def chunk_file(path):
    """Paragraph-aware chunks: never cut mid-paragraph, merge short ones up to CHUNK_CHARS.
    Every chunk carries its METADATA (source page + position) - the Lakeside exercise, for real."""
    text = open(path, encoding="utf-8").read()
    paras = [p.strip() for p in text.split("\n\n") if len(p.strip()) > 40]
    chunks, buf = [], ""
    for p in paras:
        if buf and len(buf) + len(p) > CHUNK_CHARS:
            chunks.append(buf); buf = p
        else:
            buf = (buf + "\n" + p).strip()
    if buf: chunks.append(buf)
    src = os.path.basename(path).replace(".txt", "")
    return [{"source": src, "i": n, "text": c} for n, c in enumerate(chunks)]

def build_index(dry=False):
    files = sorted(glob.glob(os.path.join(CORPUS_DIR, "*.txt")))
    chunks = [c for f in files for c in chunk_file(f)]
    sizes = [len(c["text"]) for c in chunks]
    print(f"{len(files)} files -> {len(chunks)} chunks "
          f"(avg {sum(sizes)//len(sizes)} chars, max {max(sizes)})")
    if dry:
        print("\nexample chunk:\n" + "-"*60 + f"\n[{chunks[7]['source']} #{chunks[7]['i']}]\n{chunks[7]['text'][:500]}")
        return
    t0 = time.time()
    for start in range(0, len(chunks), 32):                       # embed in batches
        batch = chunks[start:start+32]
        vecs = ollama.embed(model=EMBED_MODEL, input=[DOC_PREFIX + c["text"] for c in batch]).embeddings
        for c, v in zip(batch, vecs): c["vec"] = v
        print(f"  embedded {min(start+32, len(chunks))}/{len(chunks)}", end="\r")
    json.dump({"embed_model": EMBED_MODEL, "chunks": chunks}, open(INDEX_FILE, "w"))
    print(f"\nwrote {INDEX_FILE}  ({os.path.getsize(INDEX_FILE)//1024} KB, "
          f"{len(chunks[0]['vec'])} dims, {time.time()-t0:.1f}s)")

# ------------------------------------------------------------------ retrieval
def cosine(a, b):
    dot = sum(x*y for x, y in zip(a, b))
    return dot / (math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(y*y for y in b)) + 1e-9)

def retrieve(question, k=TOP_K):
    idx = json.load(open(INDEX_FILE))
    if idx["embed_model"] != EMBED_MODEL:
        sys.exit(f"index was built with {idx['embed_model']}, but EMBED_MODEL={EMBED_MODEL}. Re-run index.")
    q = ollama.embed(model=EMBED_MODEL, input=[QUERY_PREFIX + question]).embeddings[0]
    scored = sorted(((cosine(q, c["vec"]), c) for c in idx["chunks"]), key=lambda t: -t[0])
    return scored[:k]

def show(hits):
    for rank, (score, c) in enumerate(hits, 1):
        print(f"\n[{rank}] score={score:.3f}  source={c['source']} #{c['i']}")
        print("    " + c["text"][:400].replace("\n", "\n    ") + (" …" if len(c["text"]) > 400 else ""))

# ------------------------------------------------------------------ generation
def ask(question, use_rag=True, k=TOP_K, runs=1):
    """runs>1: repeat the generation step and print only the answers - the pass^k preview."""
    if use_rag:
        hits = retrieve(question, k)
        print(f"RETRIEVED (top {k}):"); show(hits)
        passages = "\n\n".join(f"[{r}] (from {c['source']})\n{c['text']}" for r, (_, c) in enumerate(hits, 1))
        system = ("You answer questions about a university course using only the passages you are given. "
                  "If the passages do not answer the question, reply: Not in the course documents.")
        user = (f"Passages:\n\n{passages}\n\nQuestion: {question}\n\n"
                "Answer in one or two sentences, then write the passage number you used in brackets.")
    else:
        system = "You are a helpful assistant. Answer in two sentences."
        user = question
    label = ("OPEN BOOK" if use_rag else "CLOSED BOOK") + f" ({MODEL})"
    for n in range(1, runs + 1):
        msg = ollama.chat(model=MODEL, messages=[{"role": "system", "content": system},
                                                 {"role": "user", "content": user}]).message
        text = (msg.content or "").strip().replace("\n", "\n  ")
        print(f"\n{label}" + (f" run {n}/{runs}" if runs > 1 else "") + ":\n  " + text)

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args: sys.exit(__doc__)
    cmd, flags = args[0], [a for a in args[1:] if a.startswith("--")]
    rest = " ".join(a for a in args[1:] if not a.startswith("--"))
    if cmd == "index":  build_index(dry="--dry" in flags)
    elif cmd == "search": show(retrieve(rest))
    elif cmd == "ask":
        runs = next((int(f.split("=")[1]) for f in flags if f.startswith("--runs=")), 1)
        ask(rest, use_rag="--no-rag" not in flags, runs=runs)
    else: sys.exit(__doc__)
