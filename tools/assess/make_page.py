"""Wrap the Assess body in the existing site shell; add its nav entry to every page."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
NAV = '    <li><a href="assess.html"><span class="n">&#9656;</span> Assess &amp; Mock Papers</a></li>'


def add_nav(html):
    head, separator, rest = html.partition('<main>')
    if 'href="assess.html"' not in head:
        head, count = re.subn(r'(^\s*<li><a href="practice\.html"[^\n]*$)',
                             lambda m: m[0]+'\n'+NAV, head, count=1, flags=re.M)
        if count != 1: raise ValueError('Cannot locate Practice Arena navigation')
    return head+separator+rest


def main():
    shell = (ROOT/'exam-papers.html').read_text(encoding='utf-8')
    head = shell[:shell.index('<main>')+len('<main>')]
    foot = shell[shell.index('<footer>'):]
    head = re.sub(r'<title>.*?</title>', '<title>Assess: Tests and Mock Papers</title>', head, count=1)
    head = re.sub(r'(<meta name="description" content=")[^"]*',
                  r'\g<1>Set timed tests and TMUA or MAT mock papers drawn from the official archives, then mark your students\' answers.', head, count=1)
    head = re.sub(r'(<a href="[^"]+") class="active"', r'\1', head)
    head = add_nav(head).replace('<a href="assess.html">', '<a href="assess.html" class="active">')
    body = (ROOT/'bodies/assess.html').read_text(encoding='utf-8')
    (ROOT/'assess.html').write_text(head+'\n'+body+'\n'+foot, encoding='utf-8')
    for path in ROOT.glob('*.html'):
        html = path.read_text(encoding='utf-8')
        if '<main>' not in html: continue
        updated = add_nav(html)
        if updated != html: path.write_text(updated, encoding='utf-8')
    print('Built Assess page and updated site navigation')


if __name__ == '__main__':
    main()
