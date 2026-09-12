"""Wrap the TMUA body in the existing site shell; add its separate nav entry."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAV = '    <li><a href="tmua-database.html"><span class="n">&#9656;</span> TMUA Database</a></li>'


def add_nav(html):
    head, separator, rest = html.partition('<main>')
    if 'href="tmua-database.html"' not in head:
        head, count = re.subn(r'(^\s*<li><a href="mat-database\.html"[^\n]*$)',
                             lambda m: m[0]+'\n'+NAV, head, count=1, flags=re.M)
        if count != 1: raise ValueError('Cannot locate database navigation')
    return head+separator+rest


def main():
    shell = (ROOT/'exam-papers.html').read_text(encoding='utf-8')
    head = shell[:shell.index('<main>')+len('<main>')]
    foot = shell[shell.index('<footer>'):]
    head = re.sub(r'<title>.*?</title>', '<title>TMUA Questions Database</title>', head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*',
                  r'\g<1>All 360 TMUA archive questions, 2016–2023 and early specimens, searchable by topic, paper and year with official worked solutions.', head, count=1)
    head = re.sub(r'(<a href="[^"]+") class="active"', r'\1', head)
    head = add_nav(head).replace('<a href="tmua-database.html">',
                                '<a href="tmua-database.html" class="active">')
    body = (ROOT/'bodies/tmua-database.html').read_text(encoding='utf-8')
    (ROOT/'tmua-database.html').write_text(head+'\n'+body+'\n'+foot, encoding='utf-8')
    for path in ROOT.glob('*.html'):
        html = path.read_text(encoding='utf-8')
        updated = add_nav(html)
        if updated != html: path.write_text(updated, encoding='utf-8')
    print('Built TMUA page and updated site navigation')


if __name__ == '__main__':
    main()
