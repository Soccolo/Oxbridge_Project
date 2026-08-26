"""Segment each MAT paper PDF into individual questions with page/region bounds."""
import os, re, sys, json, string
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
from manifest import PAPERS
from matlib import page_lines, content_bounds, clean, FURNITURE

HERE     = os.path.dirname(os.path.abspath(__file__))
PAPERDIR = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "papers"))
DATADIR  = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "data"))

MC_RE     = re.compile(r"^([A-J])\.(?:\s|$)")
LONG_RE   = re.compile(r"^([2-9])\.(?:\s|$)")
MODERN_RE = re.compile(r"^Question\s+(\d+)\s*([XY])?\s*$", re.I)

# 2018's question pages carry no text layer (the glyphs are vector outlines), so
# its layout is pinned by hand from the rendered pages: two multiple-choice parts
# per page on pp.5-9, then one long question per page. Pages here are 1-based.
MAP_2018 = {"mc_pages": [5, 6, 7, 8, 9],
            "long_pages": {"Q2": 10, "Q3": 12, "Q4": 14, "Q5": 16, "Q6": 18, "Q7": 20}}


def fmt_of(pid):
    if pid in ("2024", "2025"):
        return "modern"
    if pid.endswith("b"):
        return "extra"
    return "classic"


def content_rects(page):
    """Drawing/image rects that are real content, not rules or page frames."""
    out = []
    for dr in page.get_drawings():
        r = dr["rect"]
        if r.height < 2 and r.width > 200:
            continue                                   # horizontal rule
        if r.width < 2 and r.height > 200:
            continue                                   # vertical rule
        if r.width > 500 and r.height > 600:
            continue                                   # page frame
        if r.is_empty or r.is_infinite:
            continue
        out.append(r)
    for img in page.get_images(full=True):
        try:
            out.extend(page.get_image_rects(img[0]))
        except Exception:
            pass
    return out


def scan_pages(doc):
    pages = []
    for pi, page in enumerate(doc):
        ls = page_lines(page)
        real = [l for l in ls if not FURNITURE.match(l["text"])]
        top, bottom = content_bounds(page, ls)
        minx = min((l["x0"] for l in real), default=0.0)
        pages.append({"idx": pi, "lines": ls, "real": real, "top": top, "bottom": bottom,
                      "minx": minx, "h": page.rect.height, "w": page.rect.width,
                      "rects": content_rects(page)})
    return pages


def extent(pg, top, bottom, use_text=True):
    """Tight vertical span of content inside [top, bottom]; None if empty."""
    ys = []
    if use_text:
        for ln in pg["real"]:
            if ln["y0"] >= top - 2 and ln["y1"] <= bottom + 2:
                ys += [ln["y0"], ln["y1"]]
    for r in pg["rects"]:
        if r.y0 >= top - 2 and r.y1 <= bottom + 2:
            ys += [r.y0, r.y1]
    return (min(ys), max(ys)) if ys else None


def find_markers(pages, fmt):
    """Locate question starts, enforcing document order to reject false positives."""
    found, seen = [], set()
    mc_seq = list(string.ascii_uppercase[:10])
    long_seq = [str(n) for n in range(2, 10)]
    mc_i = long_i = 0
    for pg in pages:
        for ln in pg["real"]:
            t = ln["text"]
            if ln["x0"] > pg["minx"] + 6:              # markers hug the left margin
                continue
            if fmt == "modern":
                m = MODERN_RE.match(t)
                if m:
                    code = "Q" + m.group(1) + (m.group(2).upper() if m.group(2) else "")
                    if code not in seen:
                        seen.add(code)
                        found.append({"code": code, "kind": "long", "page": pg["idx"],
                                      "y": ln["y0"], "line": t})
                continue
            m = MC_RE.match(t)
            if m and mc_i < len(mc_seq) and m.group(1) == mc_seq[mc_i]:
                found.append({"code": "Q1" + m.group(1), "kind": "mc", "page": pg["idx"],
                              "y": ln["y0"], "line": t})
                mc_i += 1
                continue
            if fmt == "classic":
                m = LONG_RE.match(t)
                if m and long_i < len(long_seq) and m.group(1) == long_seq[long_i]:
                    found.append({"code": "Q" + m.group(1), "kind": "long", "page": pg["idx"],
                                  "y": ln["y0"], "line": t})
                    long_i += 1
    return found


def regions_for(markers, i, pages):
    """Rectangles covering question i, skipping blank working pages."""
    start = markers[i]
    if i + 1 < len(markers):
        end_pg, end_y = markers[i + 1]["page"], markers[i + 1]["y"]
    else:
        end_pg, end_y = len(pages) - 1, None
    regions = []
    for pi in range(start["page"], end_pg + 1):
        pg = pages[pi]
        if not pg["real"]:                 # working/blank page - never part of a question
            continue
        top = start["y"] - 5 if pi == start["page"] else pg["top"]
        bottom = (end_y - 3 if end_y is not None else pg["bottom"]) if pi == end_pg else pg["bottom"]
        ext = extent(pg, top, bottom)
        if not ext or ext[1] - ext[0] < 12:
            continue
        regions.append({"page": pi,
                        "top": round(max(top, ext[0] - 5), 1),
                        "bottom": round(min(bottom, ext[1] + 7), 1)})
    return regions


def clusters(pg, tol=3.5):
    """Group vector glyph rects into text-line bands (used for 2018 only).

    The 0.90 cut drops the centred page-number footer (y ~= 768 on an 842pt
    page) while keeping genuine content, which runs to y ~= 738 at the most.
    """
    rs = sorted([r for r in pg["rects"] if r.height < 60 and r.y1 < pg["h"] * 0.90],
                key=lambda r: r.y0)
    out = []
    for r in rs:
        if out and r.y0 <= out[-1][1] + tol:
            out[-1][1] = max(out[-1][1], r.y1)
            out[-1][2] += 1
        else:
            out.append([r.y0, r.y1, 1])
    # A trailing sparse band low on the page is the "Turn over" rubric, not content.
    while len(out) > 1 and out[-1][2] < 20 and out[-1][0] > pg["h"] * 0.80:
        out.pop()
    return out


def segment_2018(pages):
    """Page-pinned segmentation for the one paper with no text layer."""
    qs, letters, li = [], list(string.ascii_uppercase[:10]), 0
    for pno in MAP_2018["mc_pages"]:                   # two MC parts per page
        cl = clusters(pages[pno - 1])
        if len(cl) < 2:
            continue
        # Split at the widest gap, but never one that leaves a sliver behind.
        ranked = sorted(((cl[j + 1][0] - cl[j][1], j) for j in range(len(cl) - 1)),
                        reverse=True)
        k = ranked[0][1]
        for _, j in ranked:
            if cl[j][1] - cl[0][0] >= 25 and cl[-1][1] - cl[j + 1][0] >= 25:
                k = j
                break
        for grp in (cl[:k + 1], cl[k + 1:]):
            qs.append({"code": "Q1" + letters[li], "kind": "mc", "marker_line": "",
                       "regions": [{"page": pno - 1, "top": round(grp[0][0] - 6, 1),
                                    "bottom": round(grp[-1][1] + 8, 1)}], "text": ""})
            li += 1
    for code, pno in MAP_2018["long_pages"].items():
        cl = clusters(pages[pno - 1])
        if not cl:
            continue
        qs.append({"code": code, "kind": "long", "marker_line": "",
                   "regions": [{"page": pno - 1, "top": round(cl[0][0] - 6, 1),
                                "bottom": round(cl[-1][1] + 8, 1)}], "text": ""})
    return qs


def text_in(regions, pages):
    out = []
    for r in regions:
        for ln in pages[r["page"]]["real"]:
            if ln["y0"] >= r["top"] - 2 and ln["y1"] <= r["bottom"] + 2:
                out.append(ln["text"])
    return clean(" ".join(out)).strip()


def main():
    result, report = {}, []
    for pid, label, *_ in PAPERS:
        doc = fitz.open(os.path.join(PAPERDIR, pid + "-paper.pdf"))
        fmt, pages = fmt_of(pid), scan_pages(doc)
        if pid == "2018":
            qs = segment_2018(pages)
        else:
            markers = find_markers(pages, fmt)
            qs = []
            for i, mk in enumerate(markers):
                regs = regions_for(markers, i, pages)
                qs.append({"code": mk["code"], "kind": mk["kind"],
                           "marker_line": mk["line"][:150], "regions": regs,
                           "text": text_in(regs, pages)})
        result[pid] = {"label": label, "format": fmt, "pages": doc.page_count,
                       "questions": qs}
        nreg = sum(len(q["regions"]) for q in qs)
        report.append("{:6s} {:8s} n={:3d} regions={:3d}  {}".format(
            pid, fmt, len(qs), nreg, ",".join(q["code"] for q in qs)[:66]))
        doc.close()
    os.makedirs(DATADIR, exist_ok=True)
    with open(os.path.join(DATADIR, "segments.json"), "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=1)
    print("\n".join(report))
    print("\nTOTAL questions: {}".format(sum(len(v["questions"]) for v in result.values())))


if __name__ == "__main__":
    main()
