"""Locate each question's solution inside the official solution PDFs.

The solution documents are far less consistent than the papers. Across the years
a heading may be written "F.", "E:", an outdented bare "E ", a letter alone on its
line, "1. A." on the specimens, "QUESTION 2:" in 2007 - or omitted entirely, as in
2021, where each long solution simply opens a fresh page at part (i). Each
convention is tried in turn; anything that still cannot be segmented confidently
falls back to a whole-document page link.
"""
import os, re, sys, json, string, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import fitz
from manifest import PAPERS
from segment import scan_pages, regions_for, fmt_of, text_in

HERE     = os.path.dirname(os.path.abspath(__file__))
PAPERDIR = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "papers"))
DATADIR  = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "data"))

# The "$" branch lets a marker be alone on its line ("D") without also matching
# an ordinary word ("Dog"), which has neither a separator nor a line end after it.
MARK_RE     = re.compile(r"^([A-J2-9])(\.|:|\s+|$)\s*(.*)$")
MODERN_RE   = re.compile(r"^(?:Question|Q)\s*(\d+)\s*([XY])?\b", re.I)
QUESTION_RE = re.compile(r"^QUESTION\s+([2-9])\b", re.I)
PART_I_RE   = re.compile(r"^\(?i\)")
PREAMBLE_RE = re.compile(r"^Different alternative solutions", re.I)
Q1_PREFIX   = re.compile(r"^1\.\s*")            # specimens head parts as "1. A."


def body_column(pages):
    """The x-offset most lines in the document start at; markers sit left of it.

    Measured document-wide rather than per page: a page that happens to be mostly
    displayed equations would otherwise report a misleading body indent.
    """
    counts = collections.Counter(round(l["x0"]) for pg in pages for l in pg["real"])
    return float(counts.most_common(1)[0][0]) if counts else 0.0


def find_long_markers(flat, pages, windows, accepted, n_long):
    """Locate the Q2..Qn solutions, trying each heading convention in turn."""
    seq = [str(n) for n in range(2, 2 + n_long)]

    def by_pattern(window, match):
        got, want_i = [], 0
        for _, pidx, ln in window:
            ch = match(ln)
            if ch is None or ch not in seq:
                continue
            j = seq.index(ch)
            if j >= want_i:
                got.append({"code": "Q" + ch, "page": pidx, "y": ln["y0"]})
                want_i = j + 1
        return got

    def plain(ln):
        m = MARK_RE.match(ln["text"])
        if not m or not accepted(ln, m.group(2)):
            return None
        # "2." must open a question - "(i)", "[3 marks]", prose, or a bare number -
        # so that a stray line of algebra beginning "2." is not mistaken for one.
        rest = m.group(3)
        if rest and not re.match(r"^[(\[A-Z]|^\d+\.", rest):
            return None
        return m.group(1)

    def worded(ln):
        m = QUESTION_RE.match(ln["text"])
        return m.group(1) if m else None

    def page_starts(window):
        """No headings at all: each long solution opens a fresh page at part (i).

        Part (i) may trail a line or two of rubric about alternative solutions, so
        look at the top few lines rather than only the first.
        """
        out, seen = [], set()
        for _, pidx, _ in window:
            if pidx in seen:
                continue
            seen.add(pidx)
            for ln in pages[pidx]["real"][:4]:
                if PART_I_RE.match(ln["text"]):
                    out.append({"page": pidx, "y": ln["y0"]})
                    break
        return [{"code": "Q" + seq[k], "page": s["page"], "y": s["y"]}
                for k, s in enumerate(out)]

    def plausible(got):
        # Long solutions run to about a page each, so a full set that all landed on
        # one page is a numbered list inside a solution, not six question headings.
        return (len(got) == n_long
                and len({g["page"] for g in got}) >= max(2, (n_long + 1) // 2))

    best = []
    for window in windows:
        for got in (by_pattern(window, plain), by_pattern(window, worded),
                    page_starts(window)):
            if plausible(got):
                return got
            if len(got) > len(best):
                best = got
    return best                       # best effort; caller falls back to page links


def find_solution_markers(pages, fmt, n_long=6):
    flat = [(pg["idx"], ln) for pg in pages for ln in pg["real"]]

    if fmt == "modern":
        found, seen = [], set()
        for pidx, ln in flat:
            m = MODERN_RE.match(ln["text"])
            if m:
                code = "Q" + m.group(1) + (m.group(2).upper() if m.group(2) else "")
                if code not in seen:
                    seen.add(code)
                    found.append({"code": code, "page": pidx, "y": ln["y0"]})
        return found

    bx = body_column(pages)

    def accepted(ln, sep):
        # A heading always sits at (or left of) the body margin, never indented
        # like displayed algebra. Beyond that, an explicit "A." / "A:" is
        # unambiguous, while a bare "A Something" must be outdented, as prose
        # running to the body margin never is.
        if ln["x0"] > bx + 2:
            return False
        return sep in ".:" or ln["x0"] < bx - 3

    mc_seq = list(string.ascii_uppercase[:10])
    found, mc_i, first_mc, last_mc = [], 0, None, -1
    for i, (pidx, ln) in enumerate(flat):
        m = MARK_RE.match(Q1_PREFIX.sub("", ln["text"]))
        if not m:
            continue
        ch, sep = m.group(1), m.group(2)
        if ch not in mc_seq or not accepted(ln, sep):
            continue
        j = mc_seq.index(ch)
        if j >= mc_i:
            found.append({"code": "Q1" + ch, "page": pidx, "y": ln["y0"]})
            mc_i, last_mc = j + 1, i
            if first_mc is None:
                first_mc = i

    if fmt != "classic":
        return found

    # Prefer looking after the whole of Q1; if that comes up short, allow the
    # search to start right after Q1's first part instead.
    after_last = [(i, p, l) for i, (p, l) in enumerate(flat) if i > last_mc]
    after_first = [(i, p, l) for i, (p, l) in enumerate(flat)
                   if first_mc is not None and i > first_mc]
    windows = [after_last] + ([after_first] if after_first else [])
    return found + find_long_markers(flat, pages, windows, accepted, n_long)


def main():
    segs = json.load(open(os.path.join(DATADIR, "segments.json"), encoding="utf-8"))
    out, report = {}, []
    for pid, label, *_ in PAPERS:
        doc = fitz.open(os.path.join(PAPERDIR, pid + "-solutions.pdf"))
        fmt = fmt_of(pid)
        pages = scan_pages(doc)
        want = [q["code"] for q in segs[pid]["questions"]]
        n_long = sum(1 for c in want if not c.startswith("Q1"))
        markers = find_solution_markers(pages, fmt, n_long)
        got = [m["code"] for m in markers]
        complete = sorted(got) == sorted(want) and len(got) == len(set(got))
        entry = {"pages": doc.page_count, "complete": complete, "solutions": {}}
        if complete:
            order = sorted(markers, key=lambda m: (m["page"], m["y"]))
            for i, mk in enumerate(order):
                regs = regions_for(order, i, pages)
                entry["solutions"][mk["code"]] = {"regions": regs,
                                                  "page": mk["page"] + 1,
                                                  "text": text_in(regs, pages)}
        else:
            for mk in markers:
                entry["solutions"][mk["code"]] = {"regions": [], "page": mk["page"] + 1,
                                                  "text": ""}
        out[pid] = entry
        report.append("{} {:6s} {:2d}/{:2d}  {}".format(
            "OK  " if complete else "PART", pid, len(got), len(want),
            "" if complete else "missing: " + ",".join(c for c in want if c not in got)[:44]))
        doc.close()
    with open(os.path.join(DATADIR, "solutions.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print("\n".join(report))
    print("\n{}/{} solution PDFs fully segmented".format(
        sum(1 for v in out.values() if v["complete"]), len(out)))


if __name__ == "__main__":
    main()
