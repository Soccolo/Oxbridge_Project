"""Render question/solution crops and emit the independent TMUA static database."""
import argparse
import datetime
import json
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT/'tools/mat'))
from render import render_question, paper_margins
from tag import classify
from taxonomy import TOPICS as MAT_TOPICS

TOPICS = [(tid, label, chapter) for tid, label, chapter, _ in MAT_TOPICS
          if tid not in ('vectors', 'algorithms')]
TOPICS += [('functions', 'Functions', 'functions.html'),
           ('geometry', 'Geometry &amp; mensuration', 'geometry.html'),
           ('statistics', 'Statistics', 'counting.html')]
DATA = ROOT/'tmua/data'


def load_overrides(known_ids):
    path = DATA/'overrides.json'
    overrides = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    topics = {t[0] for t in TOPICS}
    for key, values in overrides.items():
        if key.startswith('_'): continue
        if key not in known_ids: raise ValueError(f'Unknown question: {key}')
        if not isinstance(values, list) or not values or any(t not in topics for t in values):
            raise ValueError(f'Invalid topics on {key}: {values}')
    return overrides


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-render', action='store_true', help='Update tags/data using existing crops')
    args = parser.parse_args()
    manifest = json.loads(Path(__file__).with_name('manifest.json').read_text())
    segments = json.loads((DATA/'segments.json').read_text(encoding='utf-8'))
    ids = {f'{pid}-{q["code"]}' for pid, s in segments.items() for q in s['paper']}
    overrides = load_overrides(ids)
    papers, questions = {}, []
    for p in sorted(manifest['papers'], key=lambda p: (-(p['year'] or 0), p['number'])):
        pid = p['id']; seg = segments[pid]
        meta = dict(p, paper=f'tmua/papers/{pid}-paper.pdf',
                    solutions=f'tmua/papers/{pid}-solutions.pdf',
                    answer_key=f'tmua/papers/{p["session"]}-answer-keys.pdf')
        papers[pid] = meta
        sizes = {}
        (ROOT/f'tmua/img/{pid}').mkdir(parents=True, exist_ok=True)
        for kind in ('paper', 'solutions'):
            with fitz.open(ROOT/meta[kind]) as doc:
                left, right = paper_margins(doc, seg[kind])
                for q in seg[kind]:
                    relative = f'tmua/img/{pid}/{"sol-" if kind == "solutions" else ""}{q["code"]}.png'
                    dest = ROOT/relative
                    if args.skip_render:
                        pix = fitz.Pixmap(dest)
                        info = dict(w=pix.width, h=pix.height)
                    else:
                        info = render_question(doc, q, left, right, dest)
                    if not info: raise ValueError(f'Missing crop: {relative}')
                    sizes[kind, q['code']] = dict(path=relative, **info)
        for q, sol in zip(seg['paper'], seg['solutions']):
            assert q['code'] == sol['code']
            qid = f'{pid}-{q["code"]}'
            auto, _, confidence = classify(q['text'], sol['text'], 'mc')
            auto = [t for t in auto if t in {t[0] for t in TOPICS}]
            tags = overrides.get(qid, auto)
            qi, si = sizes['paper', q['code']], sizes['solutions', q['code']]
            questions.append(dict(id=qid, paper=pid, code=q['code'], number=q['number'],
                kind='mc', marks=1, topics=tags, autoTopics=auto,
                confidence='reviewed' if qid in overrides else confidence,
                img=qi['path'], iw=qi['w'], ih=qi['h'], sol=si['path'], sw=si['w'], sh=si['h'],
                ppage=q['regions'][0]['page']+1, spage=sol['regions'][0]['page']+1,
                answer=seg['answers'][q['code']], text=q['text'], stext=sol['text']))
        print(pid, '20 question + 20 solution crops', flush=True)
    db = dict(generated=datetime.date.today().isoformat(), source=manifest['source'],
              topics=[dict(id=t, label=l, chapter=c) for t,l,c in TOPICS],
              papers=papers, questions=questions)
    serialized = json.dumps(db, ensure_ascii=False, separators=(',', ':'))
    (DATA/'questions.json').write_text(serialized+'\n', encoding='utf-8')
    (DATA/'questions.js').write_text('window.TMUA_DB='+serialized+';\n', encoding='utf-8')
    print(f'{len(questions)} questions; {sum(not q["topics"] for q in questions)} untagged')


if __name__ == '__main__':
    main()
