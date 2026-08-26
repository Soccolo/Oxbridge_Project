"""Auto-tag every MAT question against the controlled topic vocabulary.

Scores come from the question text and its official solution combined, which
matters for 2018 - the only paper with no text layer, where the solution is the
sole textual evidence. Confidence is written out alongside so that weak calls can
be reviewed rather than trusted silently.
"""
import os, re, sys, json, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from manifest import PAPERS
from taxonomy import TOPICS

HERE    = os.path.dirname(os.path.abspath(__file__))
DATADIR = os.path.abspath(os.path.join(HERE, "..", "..", "mat", "data"))

COMPILED = [(tid, label, chapter,
             [(w, re.compile(p, re.I)) for w, pats in rules.items() for p in pats])
            for tid, label, chapter, rules in TOPICS]

SECONDARY_RATIO = 0.45      # keep a second topic if it scores at least this much
MAX_TOPICS = 3


def score_text(text):
    scores = {}
    for tid, _, _, pats in COMPILED:
        s = 0
        for weight, rx in pats:
            n = len(rx.findall(text))
            if n:
                s += weight * min(n, 3)
        if s:
            scores[tid] = s
    return scores


# A multiple-choice part is a couple of sentences, a long question a couple of
# pages, so the same raw score means very different things. Thresholds are
# (high_score, high_margin, medium_score) per question kind.
BANDS = {"mc": (12, 4, 6), "long": (30, 8, 14)}


def classify(qtext, stext, kind):
    # The solution restates the question's subject in words, which is exactly the
    # signal we want, but it is much longer - so damp it rather than let it swamp
    # the question's own wording.
    scores = collections.Counter()
    for tid, s in score_text(qtext).items():
        scores[tid] += s * 2
    # 2018 has no question text at all, so its solution carries the full weight
    # rather than being damped as merely corroborating.
    sol_weight = 2 if not qtext.strip() else 1
    for tid, s in score_text(stext).items():
        scores[tid] += s * sol_weight
    if not scores:
        return [], 0, "none"
    ranked = scores.most_common()
    top = ranked[0][1]
    chosen = [t for t, s in ranked if s >= top * SECONDARY_RATIO][:MAX_TOPICS]
    runner = ranked[1][1] if len(ranked) > 1 else 0
    hi, margin, med = BANDS[kind]
    if top >= hi and top - runner >= margin:
        conf = "high"
    elif top >= med:
        conf = "medium"
    else:
        conf = "low"
    return chosen, top, conf


def load_overrides():
    """Hand-checked topics that win over the auto-tagger."""
    path = os.path.join(DATADIR, "overrides.json")
    if not os.path.exists(path):
        return {}
    raw = json.load(open(path, encoding="utf-8"))
    known = {t[0] for t in TOPICS}
    out = {}
    for key, topics in raw.items():
        if key.startswith("_"):
            continue
        bad = [t for t in topics if t not in known]
        if bad:
            raise SystemExit("overrides.json: unknown topic id(s) {} on {}".format(bad, key))
        out[key] = topics
    return out


def main():
    segs = json.load(open(os.path.join(DATADIR, "segments.json"), encoding="utf-8"))
    sols = json.load(open(os.path.join(DATADIR, "solutions.json"), encoding="utf-8"))
    overrides = load_overrides()
    out, counts, confs, review = {}, collections.Counter(), collections.Counter(), []
    for pid, *_ in PAPERS:
        out[pid] = {}
        for q in segs[pid]["questions"]:
            code = q["code"]
            stext = (sols[pid]["solutions"].get(code) or {}).get("text", "")
            topics, top, conf = classify(q.get("text", ""), stext, q["kind"])
            fixed = overrides.get("{}-{}".format(pid, code))
            if fixed is not None:
                topics, conf = fixed, "reviewed"
            out[pid][code] = {"topics": topics, "score": top, "confidence": conf}
            confs[conf] += 1
            for t in topics:
                counts[t] += 1
            if conf in ("low", "none"):
                review.append((pid, code, topics, top,
                               (q.get("text") or stext)[:110]))
    with open(os.path.join(DATADIR, "tags.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)

    print("confidence:", dict(confs))
    print("\ntopic frequency:")
    for tid, label, _, _ in COMPILED:
        print("  {:15s} {:4d}  {}".format(tid, counts[tid],
                                          label.replace("&amp;", "&")))
    print("\n{} questions need review:".format(len(review)))
    for pid, code, topics, top, snippet in review[:40]:
        print("  {:6s} {:5s} score={:3d} {:28s} | {}".format(
            pid, code, top, ",".join(topics)[:28], snippet[:70]))


if __name__ == "__main__":
    main()
