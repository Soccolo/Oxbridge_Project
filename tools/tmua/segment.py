"""Locate numbered questions and worked solutions; fail on missing/duplicate items.

Coordinates use zero-based PDF pages and PDF points. Glyph maps repair missing
ToUnicode tables in the older papers for search only; images use original PDFs.
"""
import json
import re
import unicodedata
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads(Path(__file__).with_name('manifest.json').read_text())
GLYPHS = json.loads(Path(__file__).with_name('glyph_map.json').read_text())


def clean(text):
    return re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text).replace('Â', '')).strip()


def lines(page):
    broken = [f[3].split('+')[-1] for f in page.get_fonts()
              if f[2] == 'Type0' and 'ToUnicode' not in page.parent.xref_object(f[0])]
    out = []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            text = ''
            for span in line['spans']:
                value = span['text']
                if any(span['font'] == f or span['font'] in f or f in span['font'] for f in broken):
                    mapping = GLYPHS.get(span['font'], {})
                    value = ''.join(mapping.get(c, c) for c in value)
                text += value
            if clean(text):
                out.append(dict(text=clean(text), bbox=list(line['bbox'])))
    return sorted(out, key=lambda l: (round(l['bbox'][1], 1), l['bbox'][0]))


def body_lines(page, ls, solution):
    # Headers and copyright/footer bands vary by paper; all question content is
    # between y=55 and y=780. The worked-answer series has a taller header band.
    if any('BLANK PAGE' in l['text'] or 'The Triangle Building' in l['text'] for l in ls):
        return []
    top = 65 if solution else 55
    return [l for l in ls if l['bbox'][1] >= top and l['bbox'][3] <= 780
            and not re.match(r'^(?:Test of Mathematics|Version |Page \d|©|BLANK PAGE|END OF (?:PAPER|TEST)|\[?Turn over)', l['text'], re.I)]


def segment(doc, solution=False, count=20):
    pages = [body_lines(p, lines(p), solution) for p in doc]
    markers = []
    for pi, ls in enumerate(pages):
        if pi < 2: continue
        for line in ls:
            text = line['text']; x0, y0, x1, y1 = line['bbox']
            pattern = r'^Question\s+(\d+)\s*$' if solution else r'^(\d{1,2})\.?\s*(?:$|[A-Z])'
            m = re.match(pattern, text)
            if not m or (not solution and x0 > 80): continue
            n = int(m[1])
            if n == len(markers) + 1:
                # Superscripts/fractions in the opening sentence can sit above
                # the number's baseline. Include the entire opening line.
                opening = [l['bbox'][1] for l in ls if y0-16 <= l['bbox'][1] <= y0]
                markers.append(dict(number=n, page=pi, top=min(opening)-4))
    if len(markers) != count:
        raise ValueError(f'{doc.name}: expected {count} markers, got {markers}')
    result = []
    for i, start in enumerate(markers):
        end = markers[i+1] if i+1 < len(markers) else dict(page=len(doc)-1, top=780)
        regs, texts = [], []
        for pi in range(start['page'], end['page']+1):
            top = start['top'] if pi == start['page'] else (65 if solution else 55)
            bottom = end['top']-2 if pi == end['page'] else 780
            ls = [l for l in pages[pi] if l['bbox'][1] >= top and l['bbox'][3] <= bottom]
            if not ls or all(re.match(r'^\d+$', l['text']) for l in ls): continue
            # Keep all vector diagrams and mathematical marks inside the span.
            rects = [fitz.Rect(l['bbox']) for l in ls]
            for drawing in doc[pi].get_drawings():
                r = drawing['rect']
                if r.y0 >= top and r.y1 <= bottom and r.width < 550 and not r.is_empty:
                    rects.append(r)
            for image in doc[pi].get_image_info():
                r = fitz.Rect(image['bbox'])
                if r.y0 >= top and r.y1 <= bottom: rects.append(r)
            regs.append(dict(page=pi, top=round(max(top,min(r.y0 for r in rects)-5),2),
                             bottom=round(min(bottom,max(r.y1 for r in rects)+6),2)))
            texts.extend(l['text'] for l in ls)
        if not regs: raise ValueError(f'{doc.name}: empty Q{i+1}')
        result.append(dict(code=f'Q{i+1}', number=i+1, regions=regs, text=clean(' '.join(texts))))
    return result


def answer_keys(path):
    with fitz.open(path) as doc:
        answers = {}
        text = clean(' '.join(p.get_text() for p in doc))
        pairs = re.findall(r'\b(\d{1,2})\s+([A-H])\b', text)
        if len(pairs) != 40: raise ValueError(f'{path}: expected 40 answer keys')
        interleaved = pairs[0][0] == pairs[1][0]
        for number in (1, 2):
            column = pairs[number-1::2] if interleaved else pairs[(number-1)*20:number*20]
            if [int(n) for n, _ in column] != list(range(1,21)):
                raise ValueError(f'{path}, paper {number}: {column}')
            answers[number] = {f'Q{n}': a for n, a in column}
    return answers


def main():
    data = {}
    for paper in MANIFEST['papers']:
        pid = paper['id']; record = {}
        for kind in ('paper', 'solutions'):
            with fitz.open(ROOT / f'tmua/papers/{pid}-{kind}.pdf') as doc:
                record[kind] = segment(doc, kind == 'solutions', paper['count'])
        record['answers'] = answer_keys(ROOT / f'tmua/papers/{paper["session"]}-answer-keys.pdf')[paper['number']]
        data[pid] = record
        print(pid, len(record['paper']), 'questions,', len(record['solutions']), 'solutions')
    (ROOT/'tmua/data/segments.json').write_text(json.dumps(data, ensure_ascii=False, indent=1)+'\n', encoding='utf-8')


if __name__ == '__main__':
    main()
