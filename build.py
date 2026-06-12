#!/usr/bin/env python3
import os, json

PAGES = [
    # (file, nav number, nav title, page <title>, prev, next)
    ("index.html",          None, "Home",                          "Advanced Mathematics for High School — Preparing for Oxbridge"),
    ("numbers.html",        "1",  "Numbers",           "Numbers and Proof Foundations"),
    ("algebra.html",        "2",  "Algebra",        "Algebra"),
    ("sequences.html",      "3",  "Sequences",         "Sequences"),
    ("functions.html",      "4",  "Functions","Functions, Graphs, Exponentials and Logarithms"),
    ("geometry.html",       "5",  "Geometry and Trigonometry",    "Geometry and Trigonometry"),
    ("differentiation.html","6",  "Differential Calculus",        "Differential Calculus"),
    ("integration.html",    "7",  "Integrals",                    "Integrals"),
    ("counting.html",       "8",  "Counting &amp; Probability",   "Counting, Probability and Statistics"),
    ("logic.html",          "9",  "Mathematical Logic",    "Mathematical Logic and Proof"),
    ("complex.html",        "10", "Complex Numbers",              "Complex Numbers"),
    ("mechanics.html",      "11", "Mechanics (STEP)",             "Mechanics"),
    ("statistics.html",     "12", "Statistics (STEP)",            "Statistics"),
    ("exam-papers.html",    None, "TMUA Exam Papers",             "TMUA Exam Papers and Resources"),
    ("practice.html",       None, "Practice Arena",               "Practice Arena — Random TMUA-style Problems"),
]

HEAD = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="Free theory and problems covering the entire TMUA syllabus, with STEP extensions — from the book Advanced Mathematics for High School: Preparing for Oxbridge.">
<link rel="stylesheet" href="styles.css">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.css">
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/katex.min.js"></script>
<script defer src="https://cdnjs.cloudflare.com/ajax/libs/KaTeX/0.16.9/contrib/auto-render.min.js"></script>
<script>
document.addEventListener("DOMContentLoaded", function() {{
  if (window.renderMathInElement) {{
    renderMathInElement(document.body, {{
      delimiters: [
        {{left: "$$", right: "$$", display: true}},
        {{left: "\\\\[", right: "\\\\]", display: true}},
        {{left: "\\\\(", right: "\\\\)", display: false}}
      ],
      throwOnError: false
    }});
  }}
}});
function toggleNav() {{
  document.getElementById("sidenav").classList.toggle("open");
}}
</script>
</head>
<body>
<div class="shell">
<aside class="sidebar">
  <a class="brand" href="index.html">
    <span class="t1">Advanced Mathematics<br>for High School</span>
    <span class="t2">Preparing for Oxbridge · Free edition</span>
  </a>
  <button class="menu-toggle" onclick="toggleNav()" aria-expanded="false" aria-controls="sidenav">Topic menu ▾</button>
  <div id="sidenav">
  <hr>
  <p class="menu-label">TMUA topic menu</p>
  <ul class="nav">
{nav}
  </ul>
  <hr>
  <ul class="nav">
    <li><a href="exam-papers.html"{ap_active}><span class="n">▸</span> TMUA Exam Papers</a></li>
    <li><a href="practice.html"{pr_active}><span class="n">▸</span> Practice Arena</a></li>
    <li><a href="index.html#syllabus"><span class="n">▸</span> Syllabus coverage map</a></li>
  </ul>
  </div>
</aside>
<main>
"""

FOOT = """
<footer><div class="inner">
<p><em>Advanced Mathematics for High School: Preparing for Oxbridge</em>, Volume&nbsp;1 — published free online.
Past-paper questions are credited to their sources (TMUA, MAT, STEP, BMO, Mathematical Kangaroo and others) and remain the property of the respective examination boards; they are reproduced here for educational use.
</p></div></footer>
</main>
</div>
</body>
</html>
"""

def navhtml(current):
    rows = []
    for f, n, t, _ in PAGES:
        if n is None:
            continue
        cls = ' class="active"' if f == current else ""
        rows.append(f'    <li><a href="{f}"{cls}><span class="n">{n}</span> {t}</a></li>')
    return "\n".join(rows)

os.makedirs("dist", exist_ok=True)
for i, (f, n, t, title) in enumerate(PAGES):
    body_path = os.path.join("bodies", f)
    with open(body_path) as fh:
        body = fh.read()
    ap = ' class="active"' if f == "exam-papers.html" else ""
    pr = ' class="active"' if f == "practice.html" else ""
    html = HEAD.format(title=title, nav=navhtml(f), ap_active=ap, pr_active=pr) + body + FOOT
    with open(os.path.join("dist", f), "w") as out:
        out.write(html)
    print("built", f)
