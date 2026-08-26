"""Render each segmented question to a single cropped PNG.

Questions that run across a page break are stitched into one image, so every
database entry is exactly one <img>. Rendering goes via an intermediate PDF page
so the vector text stays sharp rather than being upscaled from a raster.
"""
import os, sys, json, shutil
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
from manifest import PAPERS

HERE     = os.path.dirname(os.path.abspath(__file__))
PAPERDIR = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "papers"))
DATADIR  = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "data"))
IMGDIR   = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "img"))

DPI  = 140          # ~950px wide for a standard text block
PAD  = 6            # points of whitespace around the crop


def paper_margins(doc, questions):
    """One left/right margin per paper so every crop comes out the same width."""
    lo, hi = 1e9, -1e9
    for q in questions:
        for r in q["regions"]:
            page = doc[r["page"]]
            for blk in page.get_text("dict")["blocks"]:
                if blk.get("type") != 0:
                    continue
                x0, y0, x1, y1 = blk["bbox"]
                if y1 >= r["top"] - 2 and y0 <= r["bottom"] + 2:
                    lo, hi = min(lo, x0), max(hi, x1)
            for dr in page.get_drawings():
                rr = dr["rect"]
                if rr.height < 2 and rr.width > 200:
                    continue
                if rr.width > 500 and rr.height > 600:
                    continue
                if rr.y1 >= r["top"] - 2 and rr.y0 <= r["bottom"] + 2:
                    lo, hi = min(lo, rr.x0), max(hi, rr.x1)
    if lo > hi:                                  # nothing found - use the whole page
        return 40.0, doc[0].rect.width - 40.0
    w = doc[0].rect.width
    return max(lo - PAD, 0.0), min(hi + PAD, w)


def render_question(doc, q, left, right, dest):
    regs = [r for r in q["regions"] if r["bottom"] - r["top"] > 8]
    if not regs:
        return None
    width  = right - left
    height = sum(r["bottom"] - r["top"] for r in regs) + PAD * (len(regs) - 1)
    out = fitz.open()
    page = out.new_page(width=width, height=height)
    y = 0.0
    for r in regs:
        h = r["bottom"] - r["top"]
        page.show_pdf_page(fitz.Rect(0, y, width, y + h), doc, r["page"],
                           clip=fitz.Rect(left, r["top"], right, r["bottom"]))
        y += h + PAD
    pix = page.get_pixmap(dpi=DPI, colorspace=fitz.csGRAY)
    pix.save(dest)
    out.close()
    return {"w": pix.width, "h": pix.height, "bytes": os.path.getsize(dest)}


def main():
    segs = json.load(open(os.path.join(DATADIR, "segments.json"), encoding="utf-8"))
    sols = json.load(open(os.path.join(DATADIR, "solutions.json"), encoding="utf-8"))
    if os.path.isdir(IMGDIR):
        shutil.rmtree(IMGDIR)
    os.makedirs(IMGDIR, exist_ok=True)
    total_bytes = nq = ns = 0
    report = []
    for pid, label, *_ in PAPERS:
        entry = segs[pid]
        os.makedirs(os.path.join(IMGDIR, pid), exist_ok=True)

        doc = fitz.open(os.path.join(PAPERDIR, pid + "-paper.pdf"))
        left, right = paper_margins(doc, entry["questions"])
        sizes = []
        for q in entry["questions"]:
            dest = os.path.join(IMGDIR, pid, q["code"] + ".png")
            info = render_question(doc, q, left, right, dest)
            if info:
                q["image"] = "mat/img/{}/{}.png".format(pid, q["code"])
                q["image_w"], q["image_h"] = info["w"], info["h"]
                total_bytes += info["bytes"]
                sizes.append(info["bytes"])
                nq += 1
        doc.close()

        sdoc = fitz.open(os.path.join(PAPERDIR, pid + "-solutions.pdf"))
        sol_entries = [s for s in sols[pid]["solutions"].values() if s.get("regions")]
        sl, sr = paper_margins(sdoc, [{"regions": s["regions"]} for s in sol_entries]) \
            if sol_entries else (0, 0)
        nsol = 0
        for code, s in sols[pid]["solutions"].items():
            if not s.get("regions"):
                continue
            dest = os.path.join(IMGDIR, pid, "sol-" + code + ".png")
            info = render_question(sdoc, s, sl, sr, dest)
            if info:
                s["image"] = "mat/img/{}/sol-{}.png".format(pid, code)
                s["image_w"], s["image_h"] = info["w"], info["h"]
                total_bytes += info["bytes"]
                nsol += 1
                ns += 1
        sdoc.close()

        avg = sum(sizes) // len(sizes) // 1024 if sizes else 0
        report.append("{:6s} {:2d} q  {:2d} sol  avg {:3d} KB".format(
            pid, len(sizes), nsol, avg))
    with open(os.path.join(DATADIR, "segments.json"), "w", encoding="utf-8") as f:
        json.dump(segs, f, ensure_ascii=False, indent=1)
    with open(os.path.join(DATADIR, "solutions.json"), "w", encoding="utf-8") as f:
        json.dump(sols, f, ensure_ascii=False, indent=1)
    print("\n".join(report))
    print("\n{} question + {} solution images, {:.1f} MB total".format(
        nq, ns, total_bytes / 1e6))


if __name__ == "__main__":
    main()
