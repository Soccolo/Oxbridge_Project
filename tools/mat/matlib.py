"""Shared helpers for parsing the MAT PDFs."""
import re, unicodedata

LIGATURES = {"ﬀ":"ff","ﬁ":"fi","ﬂ":"fl","ﬃ":"ffi","ﬄ":"ffl",
             "−":"-","–":"-","—":"-","‘":"'","’":"'",
             "“":'"',"”":'"'," ":" "}

def clean(s):
    """Normalise PDF text artefacts: ligatures, smart quotes, odd spacing."""
    for k, v in LIGATURES.items():
        s = s.replace(k, v)
    s = unicodedata.normalize("NFKC", s)
    return re.sub(r"[ \t]+", " ", s)

def page_lines(page):
    """Every text line on the page as {y0,y1,x0,x1,text}, in reading order."""
    out = []
    for block in page.get_text("dict")["blocks"]:
        if block.get("type") != 0:
            continue
        for line in block["lines"]:
            txt = "".join(sp["text"] for sp in line["spans"])
            if not txt.strip():
                continue
            x0, y0, x1, y1 = line["bbox"]
            out.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "text": clean(txt).strip()})
    out.sort(key=lambda l: (round(l["y0"], 1), l["x0"]))
    return out

# Page furniture that should not be cropped into a question image.
FURNITURE = re.compile(
    r"^(turn over|turn over\.?|\d{1,2}|page \d+|this page (has been )?(intentionally )?left blank"
    r"|blank page|do not write.*|.*office use only.*)$", re.I)

def content_bounds(page, lines):
    """Vertical span of real content, excluding headers/footers/page numbers."""
    h = page.rect.height
    top, bottom = 0.0, h
    for ln in lines:
        if FURNITURE.match(ln["text"]):
            if ln["y1"] < h * 0.12:
                top = max(top, ln["y1"] + 2)
            elif ln["y0"] > h * 0.86:
                bottom = min(bottom, ln["y0"] - 2)
    return top, bottom
