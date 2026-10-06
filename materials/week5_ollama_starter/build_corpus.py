"""Turn the course website into plain-text files for the Week 7 RAG lab.
Strips site chrome (logo band, nav bar, pager, footer) so page headers don't
become retrieval magnets."""
import re, html, glob, os, sys
root = sys.argv[1] if len(sys.argv) > 1 else "../course_site"
out = "corpus"; os.makedirs(out, exist_ok=True)

def drop_block(s, open_pat):
    """Remove every balanced <div …> block whose opening tag matches open_pat."""
    while True:
        m = re.search(open_pat, s)
        if not m: return s
        depth, i = 0, m.start()
        for t in re.finditer(r"<div\b|</div>", s[m.start():]):
            depth += 1 if t.group(0) == "<div" else -1
            if depth == 0:
                s = s[:m.start()] + s[m.start()+t.end():]; break
        else:
            return s

n = total = 0
for f in sorted(glob.glob(f"{root}/week[1-7]/*.html")) + [f"{root}/index.html"]:
    s = open(f, encoding="utf-8").read()
    s = re.sub(r"<script.*?</script>|<style.*?</style>|<head>.*?</head>|<footer.*?</footer>", "", s, flags=re.S)
    for cls in ("uniband", "topbar", "progress", "pager"):
        s = drop_block(s, rf'<div class="(?:wrap )?{cls}[^"]*"')
    s = re.sub(r"</(p|div|li|h\d|tr|section)>", "\n", s); s = re.sub(r"<br\s*/?>", "\n", s)
    t = html.unescape(re.sub(r"<[^>]+>", " ", s)); t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n\s*\n+", "\n\n", t).strip()
    name = f.replace(root + "/", "").replace("/", "_").replace(".html", ".txt")
    open(os.path.join(out, name), "w", encoding="utf-8").write(t); n += 1; total += len(t)
print(f"{n} files, {total:,} chars -> {out}/")
