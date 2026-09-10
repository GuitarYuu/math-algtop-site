# -*- coding: utf-8 -*-
"""Static scan: raw TeX leaking outside math containers in built HTML."""
import re, glob

pat_tex = re.compile(r"\\(begin|frac|langle|rangle|pi_|mathbb|omega|cong|hat|widetilde)")
strip_blocks = [
    re.compile(r"<mjx-container.*?</mjx-container>", re.S),
    re.compile(r'<span class="arithmatex">.*?</span>', re.S),
    re.compile(r'<div class="arithmatex">.*?</div>', re.S),
    re.compile(r"<(script|style).*?</\1>", re.S),
]
tag = re.compile(r"<[^>]+>")
leaks = 0
for f in sorted(glob.glob("site/**/*.html", recursive=True)):
    html = open(f, encoding="utf-8").read()
    clean = html
    for p in strip_blocks:
        clean = p.sub("", clean)
    text = tag.sub("", clean)
    hits = pat_tex.findall(text)
    if hits:
        leaks += 1
        examples = pat_tex.finditer(text)
        first = next(examples)
        ctx = text[max(0, first.start() - 40):first.start() + 60].replace("\n", " ")
        print(f, "LEAKS:", len(hits), "|", ctx)
print("scan complete, pages with leaks:", leaks)
