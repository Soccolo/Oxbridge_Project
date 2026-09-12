"""Check completeness, provenance, topic coverage and all rendered database assets."""
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]


def main():
    db = json.loads((ROOT/'tmua/data/questions.json').read_text(encoding='utf-8'))
    segments = json.loads((ROOT/'tmua/data/segments.json').read_text(encoding='utf-8'))
    manifest = json.loads(Path(__file__).with_name('manifest.json').read_text())
    sources = json.loads((ROOT/'tmua/data/sources.json').read_text())
    expected = {f'{p["id"]}-Q{n}' for p in manifest['papers'] for n in range(1,p['count']+1)}
    actual = [q['id'] for q in db['questions']]
    assert len(actual) == len(set(actual)) == 360
    assert set(actual) == expected
    assert len(db['papers']) == 18
    assert len(sources) == 45
    for s in sources:
        assert hashlib.sha256((ROOT/s['path']).read_bytes()).hexdigest() == s['sha256'], s['path']
        assert s['url'].startswith('https://uat-wp.s3.eu-west-2.amazonaws.com/')
    topics = {t['id'] for t in db['topics']}
    for t in db['topics']: assert (ROOT/t['chapter']).is_file()
    conclusions = 0
    for q in db['questions']:
        label = q['id']
        assert q['topics'] and set(q['topics']) <= topics, label
        assert q['confidence'] == 'reviewed', label
        assert len(q['topics']) == len(set(q['topics'])), label
        assert q['answer'] in 'ABCDEFGH', label
        assert len(q['text']) > 25 and len(q['stext']) > 60, label
        assert not re.search(r'Triangle Building|BLANK PAGE|within 15 working days', q['text']+q['stext']), label
        p = db['papers'][q['paper']]
        assert segments[q['paper']]['answers'][q['code']] == q['answer'], label
        for field,w,h in [('img','iw','ih'),('sol','sw','sh')]:
            pix = fitz.Pixmap(ROOT/q[field])
            assert (pix.width,pix.height)==(q[w],q[h]), label
            assert pix.width > 500 and pix.height > 40, label
        for field,page in [('paper','ppage'),('solutions','spage')]:
            with fitz.open(ROOT/p[field]) as doc:
                assert 1 <= q[page] <= len(doc), label
        # Independently compare explicit conclusions in worked answers to keys.
        matches = re.findall(r'(?:correct (?:answer|option) is(?: therefore)?(?: option)?|answer is(?: therefore)?(?: option)?|which is (?:option )?|hence (?:option )?)\s*([A-H])\b', q['stext'])
        if matches:
            assert matches[-1] == q['answer'], (label,q['answer'],matches[-1])
            conclusions += 1
    for path in ROOT.glob('*.html'):
        head = path.read_text(encoding='utf-8').split('<main>')[0]
        assert head.count('href="tmua-database.html"') == 1, path.name
    script = (ROOT/'tmua/data/questions.js').read_text(encoding='utf-8')
    assert json.loads(script.removeprefix('window.TMUA_DB=').rstrip(';\n')) == db
    print('PASS: 360 unique questions, 18 papers, 45 verified PDFs, 720 images, all tags reviewed')
    print(f'PASS: {conclusions} explicit worked-solution conclusions also match the answer keys')
    print('Topic coverage:', dict(Counter(t for q in db['questions'] for t in q['topics'])))


if __name__ == '__main__':
    main()
