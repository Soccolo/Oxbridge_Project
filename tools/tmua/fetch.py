"""Download the official archive, validate PDFs, and record source checksums."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.request import urlopen

import fitz

ROOT = Path(__file__).resolve().parents[2]
MANIFEST = json.loads(Path(__file__).with_name('manifest.json').read_text())


def fetch(item):
    relative, url = item
    path = ROOT / relative
    if not path.exists():
        with urlopen(url, timeout=60) as response:
            data = response.read()
        with fitz.open(stream=data, filetype='pdf') as doc:
            if doc.page_count < 1:
                raise ValueError(f'Empty PDF: {url}')
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    data = path.read_bytes()
    with fitz.open(path) as doc:
        result = dict(path=relative, url=url, pages=doc.page_count,
                      sha256=hashlib.sha256(data).hexdigest())
    print(relative, flush=True)
    return result


def main():
    files = {}
    for p in MANIFEST['papers']:
        for kind in ('paper', 'solutions'):
            files[f'tmua/papers/{p["id"]}-{kind}.pdf'] = p[kind + '_url']
        files[f'tmua/papers/{p["session"]}-answer-keys.pdf'] = p['answer_key_url']
    with ThreadPoolExecutor(max_workers=6) as pool:
        sources = list(pool.map(fetch, files.items()))
    dest = ROOT / 'tmua/data/sources.json'
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(sources, indent=2) + '\n', encoding='utf-8')
    print(f'{len(sources)} verified source PDFs')


if __name__ == '__main__':
    main()
