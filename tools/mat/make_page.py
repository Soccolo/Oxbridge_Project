"""Wrap bodies/mat-database.html in the site shell and add it to every page's nav.

The shell (head, sidebar, footer) is lifted from an existing built page rather
than from build.py, because the pages at the repository root carry nav entries -
About, the mock papers, the whiteboard - that build.py's template does not.
"""
import os, re, sys, glob

ROOT   = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                      "..", ".."))
SHELL  = os.path.join(ROOT, "exam-papers.html")
BODY   = os.path.join(ROOT, "bodies", "mat-database.html")
TARGET = os.path.join(ROOT, "mat-database.html")

TITLE = "MAT Questions Database"
DESC  = ("Every published Oxford MAT question from 2007 to 2025, searchable by "
         "topic, year and degree stream, with the official solutions.")
NAV_LI = ('    <li><a href="mat-database.html"><span class="n">&#9656;</span> '
          'MAT Database</a></li>')
EXAM_LI = re.compile(r'^\s*<li><a href="exam-papers\.html".*$', re.M)


def add_nav_link(html):
    """Insert the database link after the TMUA Exam Papers entry, once."""
    if "mat-database.html" in html:
        return html, False
    m = EXAM_LI.search(html)
    if not m:
        return html, False
    return html[:m.end()] + "\n" + NAV_LI + html[m.end():], True


def main():
    shell = open(SHELL, encoding="utf-8").read()
    body = open(BODY, encoding="utf-8").read()

    head = shell[:shell.index("<main>") + len("<main>")]
    foot = shell[shell.index("<footer>"):]

    head = re.sub(r"<title>.*?</title>", "<title>" + TITLE + "</title>", head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*(">)',
                  lambda m: m.group(1) + DESC + m.group(2), head, count=1)
    head, _ = add_nav_link(head)
    # this page owns the highlight, not the page the shell was taken from
    head = head.replace('<a href="exam-papers.html" class="active">',
                        '<a href="exam-papers.html">')
    head = head.replace('<a href="mat-database.html">',
                        '<a href="mat-database.html" class="active">')

    with open(TARGET, "w", encoding="utf-8") as f:
        f.write(head + "\n" + body + "\n" + foot)
    print("wrote", os.path.relpath(TARGET, ROOT))

    changed = 0
    for path in sorted(glob.glob(os.path.join(ROOT, "*.html"))):
        if os.path.abspath(path) == os.path.abspath(TARGET):
            continue
        html = open(path, encoding="utf-8").read()
        html, did = add_nav_link(html)
        if did:
            open(path, "w", encoding="utf-8").write(html)
            changed += 1
    print("added nav link to {} existing pages".format(changed))


if __name__ == "__main__":
    main()
