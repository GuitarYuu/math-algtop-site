# -*- coding: utf-8 -*-
"""Build the SJTU-style MkDocs site from the LaTeX review document and OCR transcriptions.

Sources:
  LaTeX review doc (sec1..sec9.tex + sec10.tex) -> docs/ch01..ch09.md + docs/checklist.md
  algtop/ocr/page_XXX.md                        -> docs/notes/pages-NNN-MMM.md

Hard rules from COURSE_IMPORT_PLAYBOOK.md applied here:
  * math regions are MASKED before any scanning/transform, restored verbatim;
  * environments are matched with a nesting-aware scanner;
  * list items keep 4-space continuations and blank lines around display math;
  * no blind punctuation replacement.
"""
from __future__ import annotations

import re
from pathlib import Path

LATEX_DIR = Path(r"C:\Users\25448\Documents\LaTeX\代数拓扑重点整理")
OCR_DIR = Path(r"C:\Users\25448\.zcode\workspace\default\algtop\ocr")
DOCS = Path(r"D:\ZCodeProjects\math-algtop-classic\docs")

CHAPTERS = [
    (1, "sec1.tex", "绪论：代数拓扑的主旨"),
    (2, "sec2.tex", "流形与曲面"),
    (3, "sec3.tex", "同伦"),
    (4, "sec4.tex", "基本群"),
    (5, "sec5.tex", "复迭空间（覆盖空间）"),
    (6, "sec6.tex", "范畴与函子"),
    (7, "sec7.tex", "奇异同调"),
    (8, "sec8.tex", "Sⁿ 的同调与映射度"),
    (9, "sec9.tex", "相对同调"),
]

# 每章一句话导语（章节题头）
CHAPTER_LEDES = {
    1: "用代数方法研究拓扑空间——不变量如何区分「同胚」与「同伦」。",
    2: "从流形、商空间到多边形表示：闭曲面的构造与完全分类。",
    3: "定端同伦、形变收缩与可缩空间——「变形」的严格语言。",
    4: "道路类的代数化：π₁ 的定义、计算与 van Kampen 定理。",
    5: "覆盖空间：提升定理群、叶数与万有复迭，计算 π₁ 的机器。",
    6: "范畴、函子与「函子保同构」——各不变量的统一语言。",
    7: "链复形、奇异同调与 Mayer–Vietoris：可计算的拓扑不变量。",
    8: "Sⁿ 的同调、映射度与 Hopf 定理：从 Brouwer 不动点到毛球定理。",
    9: "空间偶、长正合列与切除：相对化与区域不变性。",
}

# ---------------- macro expansion ----------------

MACROS = {"R": r"\mathbb{R}", "C": r"\mathbb{C}", "Z": r"\mathbb{Z}",
          "N": r"\mathbb{N}", "Q": r"\mathbb{Q}"}
MACRO_ARG = {"Sn": r"S^{{{}}}", "Dn": r"D^{{{}}}",
             "RP": r"\mathbb{{R}}P^{{{}}}", "pione": r"\pi_{{1}}({})"}
BARE = {r"\hx": r"\sim", r"\xto": r"\xrightarrow", r"\inv": r"^{-1}"}


def expand_macros(s: str) -> str:
    # \coloneqq may be absent from the bundled MathJax component
    s = s.replace(r"\coloneqq", ":=")
    for name in ("RP", "Sn", "Dn", "pione"):
        pat = re.compile(r"\\" + name + r"\{([^{}]*)\}")
        prev = None
        while prev != s:
            prev = s
            s = pat.sub(lambda m: MACRO_ARG[name].format(m.group(1)), s)
    for name, val in MACROS.items():
        s = re.sub(r"\\" + name + r"(?![a-zA-Z])", lambda m, v=val: v, s)
    for name, val in BARE.items():
        s = s.replace(name, val)
    s = (s.replace(r'M\"obius', "Möbius").replace(r'\"o', "ö")
          .replace(r'\"u', "ü").replace(r'\"a', "ä")
          .replace(r"\'e", "é").replace(r"\'a", "á"))
    return s


# ---------------- math masking ----------------

MATH_TOKEN = "\x00M{}\x00"  # token never present in source, survives text transforms
# display \[..\] first, then $$..$$, then multi-line inline $..$
MATH_ALL_RE = re.compile(r"\\\[.*?\\\]|\$\$.*?\$\$|\$[^$]+?\$", re.S)
INLINE_SINGLE = re.compile(r"\$[^$\n]+?\$")


def mask_math(text: str, store: list[str]) -> str:
    def keep(mm):
        store.append(mm.group(0))
        return MATH_TOKEN.format(len(store) - 1)
    return MATH_ALL_RE.sub(keep, text)


def unmask_math(text: str, store: list[str]) -> str:
    def repl(mm):
        return store[int(mm.group(1))]
    return re.sub("\x00M(\\d+)\x00", repl, text)


TOK_LINE = re.compile(r"^(\s*)(\x00M\d+\x00)\s*$")


def pad_tokens(text: str) -> str:
    """Blank-line-separate standalone display-math placeholder lines.

    Otherwise `\\[ .. \\]` directly after a text line is eaten by markdown's
    backslash-escape (`\\[` -> `[`), verified with a minimal repro.
    """
    lines = text.splitlines()
    out: list[str] = []
    for ln in lines:
        if TOK_LINE.match(ln):
            while out and out[-1].strip():
                out.append("")
            out.append(ln)
            out.append("")
        else:
            out.append(ln)
    return "\n".join(out)


# ---------------- text transforms (outside math only) ----------------

def transform_text(text: str) -> str:
    text = re.sub(r"\\textbf\{([^{}]*)\}", r"**\1**", text)
    text = re.sub(r"\\emph\{([^{}]*)\}", r"*\1*", text)
    text = text.replace("\\&", "&").replace("\\%", "%").replace("\\#", "#")
    text = re.sub(r"(?<=[A-Za-z0-9])--(?=[A-Za-z0-9])", "–", text)
    text = re.sub(r"<(?=[a-zA-Z/!])", "&lt;", text)
    return text


# headings cannot carry MathJax spans cleanly (Material TOC copies raw text),
# so translate the few heading formulas to plain unicode
HEAD_MATH = [
    (r"\pi_1(S^1)\cong\mathbb{Z}", "π₁(S¹)≅ℤ"),
    (r"S^n", "Sⁿ"),
    (r"H_0", "H₀"),
    (r"H_1", "H₁"),
]


def plainify_heading(title: str) -> str:
    # title may contain masked-math tokens: unmask first via caller if needed.
    t = title
    t = t.replace("$", "").replace("\\(", "").replace("\\)", "").replace("\\[", "").replace("\\]", "")
    for a, b in HEAD_MATH:
        t = t.replace(a, b)
    t = re.sub(r"\\mathbb\{([A-Z])\}", lambda m: {"R": "ℝ", "Z": "ℤ", "C": "ℂ", "N": "ℕ", "Q": "ℚ"}.get(m.group(1), m.group(1)), t)
    t = re.sub(r"\^\{(.*?)\}", lambda m: "".join({"n": "ⁿ", "1": "¹", "2": "²", "0": "⁰", "-1": "⁻¹", "*": "*"} .get(ch, ch) for ch in m.group(1)), t)
    t = re.sub(r"_(?=[0-9])", "", t)
    t = t.replace("1(S^1)", "1(S¹)") if "^1)" in t else t
    t = t.replace("S^1", "S¹").replace("\\cong", "≅").replace("\\sim", "∼").replace("\\pi", "π")
    t = t.replace("\\(", "").replace("\\)", "")
    return t.strip()


# ---------------- nesting-aware environment scanning ----------------

BEGIN_RE = re.compile(r"\\begin\{([a-zA-Z*]+)\}(\[[^\]]*\])?")
END_LEN = len("\\end{}")


def find_env_end(text: str, start: int, env: str) -> int:
    depth = 0
    for m in re.finditer(r"\\(begin|end)\{([a-zA-Z*]+)\}", text[start:]):
        if m.group(2) == env:
            depth += 1 if m.group(1) == "begin" else -1
            if depth == 0:
                return start + m.end()
    raise ValueError(f"unmatched environment: {env}")


ENV_TITLES = {"definition": "定义", "theorem": "定理", "proposition": "命题",
              "lemma": "引理", "corollary": "推论", "fact": "命题",
              "example": "例", "notation": "记号", "remark": "注"}
ADMON = {"definition": "definition", "notation": "definition",
         "theorem": "theorem", "proposition": "proposition", "lemma": "lemma",
         "corollary": "corollary", "fact": "proposition",
         "example": "example", "remark": "remark",
         "kaodian": "kaodian", "methodbox": "method", "proof": "proof"}


def strip_comments(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        out, i = [], 0
        while i < len(ln):
            if ln[i] == "\\" and i + 1 < len(ln):
                out.append(ln[i:i + 2]); i += 2; continue
            if ln[i] == "%":
                break
            out.append(ln[i]); i += 1
        lines.append("".join(out))
    return "\n".join(lines)


TOK_ONLY = re.compile(r"^(\x00M\d+\x00)+$")


def store_content(mm, store):
    return store[int(mm.group(1))]


def inline_math_text(tok_text: str, store: list[str]) -> str:
    """Render standalone display tokens as single-line $$..$$ (the only
    arithmatex-safe form inside markdown list items — verified by repro)."""
    def one(mm):
        content = store[int(mm.group(1))]
        c = content.strip()
        if c.startswith("$$"):
            inner = c[2:-2]
        elif c.startswith("\\["):
            inner = c[2:-2]
        else:
            return c
        return "$$" + re.sub(r"\s+", " ", inner).strip() + "$$"
    return re.sub("\x00M(\\d+)\x00", one, tok_text)


def convert_lists(text: str, store: list[str] | None = None) -> str:
    """\\begin/end{itemize,enumerate} + \\item -> markdown lists.

    Items keep blank lines before/after display-math placeholder lines and
    4-space continuation (playbook §三.3).
    """
    out: list[str] = []
    kind = None
    item_no = 0
    prev_blank = True
    for ln in text.splitlines():
        s = ln.strip()
        if re.match(r"\\begin\{enumerate\}$", s):
            kind, item_no = "ol", 0; continue
        if re.match(r"\\begin\{itemize\}$", s):
            kind = "ul"; continue
        if re.match(r"\\end\{(enumerate|itemize)\}$", s):
            kind = None
            if out and out[-1] != "":
                out.append("")
            continue
        if re.match(r"\\item\b", s):
            content = re.sub(r"^\\item\s*", "", s)
            if kind == "ol":
                item_no += 1
                out.append(f"{item_no}. {content}")
            else:
                out.append(f"- {content}")
            prev_blank = False
            continue
        if kind is not None and s:
            if store is not None and TOK_ONLY.match(s):
                merged = inline_math_text(s, store)
                if out and out[-1].strip():
                    out[-1] += " " + merged
                else:
                    out.append("    " + merged)
                prev_blank = False
                continue
            if s.startswith("$$") and out and out[-1] != "":
                out.append("")
            out.append("    " + s)
            if s.endswith("$$"):
                out.append("")
            prev_blank = False
            continue
        if not s:
            if out and out[-1] != "":
                out.append("")
            prev_blank = True
            continue
        out.append(ln)
        prev_blank = False
    return "\n".join(out)


def display_math_pass(text: str) -> str:
    """Turn \\[ .. \\] into fenced $$ blocks (outside lists)."""
    return re.sub(r"\\\[\s*(.*?)\s*\\\]",
                  lambda mm: "\n\n$$\n" + mm.group(1).strip() + "\n$$\n\n",
                  text, flags=re.S)


class SectionParser:
    def __init__(self, secno: int | None, src: str):
        self.secno = secno
        self.counter = 0
        self.subcounter = 0
        self.labels: dict[str, str] = {}
        self.out: list[str] = []
        self.mathstore: list[str] = []

    def next_number(self) -> str:
        self.counter += 1
        return f"{self.secno}.{self.counter}"

    def run(self, src: str) -> str:
        src = strip_comments(src)
        src = expand_macros(src)
        src = mask_math(src, self.mathstore)
        src = re.sub(r"\n{3,}", "\n\n", src).strip()
        pos = 0
        while True:
            m = BEGIN_RE.search(src, pos)
            if not m:
                self.emit_text(src[pos:])
                break
            self.emit_text(src[pos:m.start()])
            env, opt = m.group(1), (m.group(2) or "").strip("[]").strip()
            end = find_env_end(src, m.start(), env)
            body = src[m.end():end - END_LEN - len(env)]
            self.handle_env(env, opt, body)
            pos = end
        out = "\n".join(self.out)
        out = re.sub(r"\\ref\{([^{}]+)\}", lambda mm: self.labels.get(mm.group(1), "**" + mm.group(1) + "**"), out)
        out = re.sub(r"\\label\{[^{}]*\}", "", out)
        out = re.sub(r"\n{3,}", "\n\n", out)
        return unmask_math(out, self.mathstore)

    # ---- free text ----
    def emit_text(self, text: str) -> None:
        if not text.strip():
            return
        # subsections (numbered or starred), record their labels
        def sub_header(mm):
            label = mm.group(3)
            title = plainify_heading(unmask_math(mm.group(2), self.mathstore))
            if mm.group(1):
                num = None
                text_out = f"## {title}"
            else:
                self.subcounter += 1
                num = f"{self.secno}.{self.subcounter}"
                text_out = f"## {num} {title}"
            if label and num:
                self.labels[label] = num
            return text_out
        text = re.sub(r"\\subsection(\*?)\{([^{}]*)\}(?:\\label\{([^{}]*)\})?", sub_header, text)
        text = re.sub(r"\\section(\*?)\{([^{}]*)\}(?:\\label\{([^{}]*)\})?",
                      lambda mm: (self.labels.update({mm.group(3): str(self.secno)}) if mm.group(3) and self.secno else None) and "" or "", text)
        text = re.sub(r"\\section\*?\{[^{}]*\}", "", text)
        text = re.sub(r"\\label\{[^{}]*\}", "", text)
        text = re.sub(r"\\addcontentsline\{[^{}]*\}\{[^{}]*\}\{[^{}]*\}", "", text)
        text = re.sub(r"\\renewcommand\{[^{}]*\}\{[^{}]*\}", "", text)
        text = re.sub(r"\\vspace\{[^{}]*\}", "", text)
        text = convert_lists(text, self.mathstore)
        text = display_math_pass(text)
        text = transform_text(text)
        text = pad_tokens(text)
        self.out.append(text.strip() + "\n")

    # ---- environments ----
    def handle_env(self, env: str, opt: str, body: str) -> None:
        if env in ENV_TITLES:
            num = self.next_number()
            title = f"{ENV_TITLES[env]} {num}" + (f"（{opt}）" if opt else "")
            for lab in re.finditer(r"\\label\{([^{}]+)\}", body):
                self.labels[lab.group(1)] = num
            self.out.append(self.admonition(ADMON[env], title, body))
        elif env in ("kaodian", "methodbox"):
            title = "考点提示" if env == "kaodian" else "常用方法与结论"
            self.out.append(self.admonition(ADMON[env], title, body))
        elif env == "proof":
            opt2 = re.sub(r"^(重要)?证明", "", opt).strip("（） ")
            title = f"证明（{opt2}）" if opt2 else "证明"
            body = re.sub(r"\\label\{[^{}]*\}", "", body)
            body = body.replace(r"\qed", "")
            self.out.append(self.admonition("proof", title, body))
        elif env in ("itemize", "enumerate"):
            text = re.sub(r"\\label\{[^{}]*\}", "", body)
            text = convert_lists(text, self.mathstore)
            text = display_math_pass(text)
            text = transform_text(text)
            text = unmask_math(text, self.mathstore)
            self.out.append(text.strip() + "\n")
        elif env in ("align", "align*", "equation", "equation*"):
            core = "aligned" if env.startswith("align") else "equation"
            self.out.append(f"\n$$\n\\begin{{{core}}}\n" + body.strip() + f"\n\\end{{{core}}}\n$$\n")
        elif env == "center":
            tab = re.search(r"\\begin\{tabular\}\{[^}]*\}(.*?)\\end\{tabular\}", body, re.S)
            if tab:
                self.out.append(self.tabular_to_md(tab.group(1)) + "\n")
            else:
                self.out.append(transform_text(body).strip() + "\n")
        else:
            self.out.append(body.strip() + "\n")

    def admonition(self, kind: str, title: str, body: str) -> str:
        body = re.sub(r"\\label\{[^{}]*\}", "", body)
        # align/equation envs nested inside theorem-like environments
        def align_repl(mm):
            return "\n\n$$\n\\begin{aligned}\n" + mm.group(2).strip() + "\n\\end{aligned}\n$$\n\n"
        body = re.sub(r"\\begin\{(align\*?|equation\*?)\}(.*?)\\end\{\1\}", align_repl, body, flags=re.S)
        inner = convert_lists(body, self.mathstore)
        inner = display_math_pass(inner)
        inner = transform_text(inner)
        inner = pad_tokens(inner)
        # restore math BEFORE indenting so multi-line displays keep the
        # admonition's 4-space prefix on every line
        inner = unmask_math(inner, self.mathstore)
        inner = re.sub(r"\n[ \t]+\n", "\n\n", inner)
        inner = re.sub(r"\n{3,}", "\n\n", inner).strip()
        return f'!!! {kind} "{title}"\n\n' + indent(inner) + "\n"

    def tabular_to_md(self, body: str) -> str:
        rows = []
        for raw in re.split(r"\\\\", body):
            raw = re.sub(r"\\hline", "", raw).strip()
            if not raw:
                continue
            cells = []
            for c in raw.split("&"):
                c = c.strip()
                # mask math so a literal | outside $..$ is escaped, and pipes
                # INSIDE math are rewritten to \vert (markdown table splitter
                # would otherwise cut the cell at them)
                c = mask_math(c, self.mathstore)
                c = transform_text(c).replace("|", "\\|")
                c = re.sub("\x00M(\\d+)\x00",
                           lambda mm: re.sub(r"\|", r"\\vert ", store_content(mm, self.mathstore)),
                           c)
                c = c.replace("\n", " ")
                cells.append(c)
            rows.append(cells)
        if not rows:
            return ""
        ncols = max(len(r) for r in rows)
        lines = ["| " + " | ".join(rows[0]) + " |", "|" + " --- |" * ncols]
        for r in rows[1:]:
            r += [""] * (ncols - len(r))
            lines.append("| " + " | ".join(r) + " |")
        return "\n".join(lines)


def indent(text: str, n: int = 4) -> str:
    pad = " " * n
    out: list[str] = []
    for ln in text.splitlines():
        out.append(pad + ln if ln.strip() else "")
    return "\n".join(out)


# ---------------- page assembly ----------------

# 每章题记：与章节主旨相扣的古文（真实出处）
EPIGRAPHS = {
    1: ("凿户牖以为室，当其无，有室之用。", "《道德经·十一章》"),
    2: ("曲成万物而不遗。", "《周易·系辞上》"),
    3: ("天下同归而殊途，一致而百虑。", "《周易·系辞下》"),
    4: ("独立而不改，周行而不殆。", "《道德经·二十五章》"),
    5: ("若网在纲，有条而不紊。", "《尚书·盘庚》"),
    6: ("枢始得其环中，以应无穷。", "《庄子·齐物论》"),
    7: ("积土成山，风雨兴焉；积水成渊，蛟龙生焉。", "《荀子·劝学》"),
    8: ("不动如山。", "《孙子兵法·军争篇》"),
    9: ("君子和而不同。", "《论语·子路》"),
}


def epigraph_md(quote: str, source: str) -> str:
    return (
        '<div class="epigraph" markdown="1">\n\n'
        f'**「{quote}」**\n\n'
        f'—— {source}\n\n'
        '</div>\n\n'
    )


def build_chapter(no: int, texname: str, title: str) -> dict[str, str]:
    parser = SectionParser(no, "")
    body = parser.run((LATEX_DIR / texname).read_text(encoding="utf-8"))
    head = f"# 第 {no} 章 {title}\n\n"
    if no in EPIGRAPHS:
        head += epigraph_md(*EPIGRAPHS[no])
    (DOCS / f"ch{no:02d}.md").write_text(head + body + "\n", encoding="utf-8")
    print(f"ch{no:02d}.md  labels={len(parser.labels)}  counter={parser.counter}")
    return parser.labels


def build_checklist() -> None:
    parser = SectionParser(None, "")
    body = parser.run((LATEX_DIR / "sec10.tex").read_text(encoding="utf-8"))
    head = "# 考前复习清单\n\n" + epigraph_md("温故而知新，可以为师矣。", "《论语·为政》")
    (DOCS / "checklist.md").write_text(head + body.strip() + "\n", encoding="utf-8")
    print("checklist.md")


# ---------------- OCR notes ----------------

def clean_ocr_page(text: str) -> str:
    text = re.sub(r"^###\s*第\s*\d+\s*页[^\n]*\n?", "", text)
    while True:
        m = re.search(r"\\xymatrix\{", text)
        if not m:
            break
        depth, i = 0, m.end() - 1
        while i < len(text):
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
                if depth == 0:
                    break
            i += 1
        text = text[:m.start()] + "[交换图（略）]" + text[i + 1:]
    # transcription pages are PLAIN-TEXT math: escape $ so arithmatex never
    # fires (OCR TeX is frequently invalid -> would show MathJax error boxes).
    # Raw TeX stays visible, faithful and searchable.
    text = text.replace("$", "&#36;")
    text = re.sub(r"<(?=[a-zA-Z/!])", "&lt;", text)
    return text.strip()


def build_notes(chunk: int = 20) -> None:
    files = sorted(OCR_DIR.glob("page_*.md"))
    for i in range(0, len(files), chunk):
        group = files[i:i + chunk]
        lo, hi = int(group[0].stem[-3:]), int(group[-1].stem[-3:])
        parts = [f"# 讲义转录 第 {lo:03d}–{hi:03d} 页\n",
                 "> 本节内容为视觉模型对扫描讲义的**自动转录（未经人工校对）**，可能有识别误差。\n"
                 "> 为忠实呈现原始记录，数学公式按转录原文以 TeX 文本显示（不渲染）；"
                 "规范化的公式表述请看「课程重点」各章。\n"]
        for f in group:
            n = int(f.stem[-3:])
            body = clean_ocr_page(f.read_text(encoding="utf-8"))
            if body:
                parts.append(f"\n---\n\n## 第 {n} 页\n\n{body}\n")
        out = DOCS / "notes" / f"pages-{lo:03d}-{hi:03d}.md"
        out.write_text("".join(parts), encoding="utf-8")
        print(out.name)


def main() -> None:
    global_labels: dict[str, str] = {}
    for no, tex, title in CHAPTERS:
        labels = build_chapter(no, tex, title)
        global_labels.update(labels)
    build_checklist()
    # resolve cross-file \ref fallbacks (e.g. sec:pi1 defined in ch04, used in ch02)
    for md in list(DOCS.glob("ch*.md")) + [DOCS / "checklist.md"]:
        t = md.read_text(encoding="utf-8")
        t2 = re.sub(r"\*\*([a-zA-Z0-9:_-]+)\*\*",
                    lambda mm: global_labels.get(mm.group(1), mm.group(0)), t)
        if t2 != t:
            md.write_text(t2, encoding="utf-8")
            print("refs resolved:", md.name)
    print("done")


if __name__ == "__main__":
    main()
