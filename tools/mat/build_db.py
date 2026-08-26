"""Merge segments, solutions and tags into the single JSON the database page loads."""
import os, re, sys, json, datetime
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifest import PAPERS
from taxonomy import TOPICS
from segment import fmt_of

HERE    = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "data"))
PAPERDIR = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "papers"))

# Which degree streams answer which question. The papers state this on their cover
# ("I have attempted Questions 1,2,3,4,5" / "1,2,3,5,6" / "1,2,5,6,7") and it held
# unchanged from 2007 to 2022; 2023 dropped Q7 and reshuffled.
ALL = ["maths", "mathscs", "cs"]
CLASSIC_STREAMS = {"Q1": ALL, "Q2": ALL, "Q3": ["maths", "mathscs"], "Q4": ["maths"],
                   "Q5": ALL, "Q6": ["mathscs", "cs"], "Q7": ["cs"]}
STREAMS_2023 = {"Q1": ALL, "Q2": ALL, "Q3": ALL, "Q4": ["maths"], "Q5": ALL,
                "Q6": ["mathscs", "cs"]}

STREAM_LABELS = {"maths": "Mathematics / Maths &amp; Stats / Maths &amp; Phil",
                 "mathscs": "Mathematics &amp; Computer Science",
                 "cs": "Computer Science / CS &amp; Philosophy"}

MARKS_RE = re.compile(r"\[(\d+)\s*marks?\]", re.I)


def year_of(pid):
    if pid.startswith("spec"):
        return 2006                      # sort the specimens before 2007
    return int(pid[:4])


def paper_meta(pid, label, fmt):
    kind = ("Specimen" if pid.startswith("spec")
            else "Extra" if fmt == "extra" else "Main")
    return {"label": label, "year": year_of(pid), "format": fmt, "series": kind,
            "paper": "mat/papers/{}-paper.pdf".format(pid),
            "solutions": "mat/papers/{}-solutions.pdf".format(pid),
            "feedback": ("mat/papers/{}-feedback.pdf".format(pid)
                         if os.path.exists(os.path.join(PAPERDIR, pid + "-feedback.pdf"))
                         else None)}


def streams_for(pid, fmt, code):
    if fmt in ("extra", "modern"):
        return ALL
    base = "Q1" if code.startswith("Q1") and len(code) > 2 else code
    table = STREAMS_2023 if pid == "2023" else CLASSIC_STREAMS
    return table.get(base, ALL)


def marks_for(fmt, kind, text):
    if fmt == "extra":
        return None                      # the Extra papers never state a mark tariff
    found = [int(m) for m in MARKS_RE.findall(text or "")]
    if kind == "long" and found:
        return sum(found)
    return 4 if kind == "mc" else 15


def main():
    segs = json.load(open(os.path.join(DATADIR, "segments.json"), encoding="utf-8"))
    sols = json.load(open(os.path.join(DATADIR, "solutions.json"), encoding="utf-8"))
    tags = json.load(open(os.path.join(DATADIR, "tags.json"), encoding="utf-8"))

    papers, questions = {}, []
    for pid, label, *_ in PAPERS:
        fmt = fmt_of(pid)
        papers[pid] = paper_meta(pid, label, fmt)
        for q in segs[pid]["questions"]:
            code = q["code"]
            sol = sols[pid]["solutions"].get(code) or {}
            tag = tags[pid].get(code) or {}
            # 2018 has no text layer, so its solution is the only text to search on.
            text = q.get("text") or sol.get("text", "")
            rec = {
                "id": "{}-{}".format(pid, code),
                "paper": pid,
                "code": code,
                "label": code.replace("Q1", "Q1", 1) if q["kind"] == "mc" else code,
                "kind": q["kind"],
                "marks": marks_for(fmt, q["kind"], q.get("text")),
                "topics": tag.get("topics", []),
                "confidence": tag.get("confidence", "none"),
                "streams": streams_for(pid, fmt, code),
                "img": q.get("image"),
                "iw": q.get("image_w"),
                "ih": q.get("image_h"),
                "sol": sol.get("image"),
                "sw": sol.get("image_w"),
                "sh": sol.get("image_h"),
                "ppage": (q["regions"][0]["page"] + 1) if q.get("regions") else None,
                "spage": sol.get("page"),
                "text": re.sub(r"\s+", " ", text)[:1400],
                # Indexed for search but never displayed, so a query can reach the
                # method a question is solved by, not just how it is worded.
                "stext": re.sub(r"\s+", " ", sol.get("text", "")),
            }
            questions.append(rec)

    db = {"generated": datetime.date.today().isoformat(),
          "source": "https://www.maths.ox.ac.uk/study-here/undergraduate-study/"
                    "maths-admissions-test",
          "topics": [{"id": t, "label": l, "chapter": c} for t, l, c, _ in TOPICS],
          "streamLabels": STREAM_LABELS,
          "papers": papers,
          "questions": questions}
    dest = os.path.join(DATADIR, "questions.json")
    with open(dest, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, separators=(",", ":"))
    # Also emit the data as a script. A <script src> is not subject to the CORS
    # rules that make fetch() fail on file://, so the page works when opened
    # straight off disk as well as when deployed.
    with open(os.path.join(DATADIR, "questions.js"), "w", encoding="utf-8") as f:
        f.write("window.MAT_DB=")
        json.dump(db, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")
    kb = os.path.getsize(dest) / 1024
    untagged = sum(1 for q in questions if not q["topics"])
    print("{} questions, {} papers -> questions.json ({:.0f} KB)".format(
        len(questions), len(papers), kb))
    print("untagged: {}   marks unknown: {}".format(
        untagged, sum(1 for q in questions if q["marks"] is None)))
    print("by kind:", {k: sum(1 for q in questions if q["kind"] == k)
                       for k in ("mc", "long")})


if __name__ == "__main__":
    main()
