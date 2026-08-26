# Advanced Mathematics for High School — Preparing for Oxbridge (free online edition)

A fully static website: no build step, no server-side code. Every page is plain
HTML + one shared stylesheet; mathematics renders in the browser via KaTeX
(loaded from the cdnjs CDN).

## Contents
- index.html            — home, about the tests, Initial Aptitude Test, syllabus map
- numbers.html          — Topic 1 (book Ch. 2)
- algebra.html          — Topic 2 (book Ch. 3)
- sequences.html        — Topic 3 (book Ch. 4)
- functions.html        — Topic 4 (book Ch. 5)
- geometry.html         — Topic 5 (NEW chapter, incl. 3D geometry)
- differentiation.html  — Topic 6 (book Ch. 6)
- integration.html      — Topic 7 (book Ch. 7, COMPLETED: definite integrals, FTC,
                          areas, trapezium rule, solids of revolution + new problems)
- counting.html         — Topic 8 (NEW: TMUA underpinning knowledge)
- logic.html            — Topic 9 (NEW: TMUA Paper 2)
- complex.html          — Extension (book Ch. 8)
- mechanics.html        — Extension, STEP (NEW chapter)
- statistics.html       — Extension, STEP (NEW chapter)
- exam-papers.html      — past-paper links and study method
- mat-database.html     — searchable Oxford MAT question database (see below)
- mock-paper-1.html     — original mock, TMUA Paper 1 (applications), 20 Q + solutions
- mock-paper-2.html     — original mock, TMUA Paper 2 (reasoning), 20 Q + solutions
- styles.css

## MAT questions database
`mat-database.html` indexes **349 questions from 25 Oxford MAT papers** — every
published test from 2007 to 2025, both specimen papers, and the four "Extra"
papers — filterable by topic, year, question type and degree stream, and
searchable across both the question text and its official solution. Each entry
shows the question as a cropped image, reveals the official solution inline, and
deep-links to the exact page of the source PDF.

    mat/papers/    the 67 source PDFs from maths.ox.ac.uk (paper, solutions, feedback)
    mat/img/       one cropped PNG per question and per solution
    mat/data/      questions.json + questions.js (what the page loads),
                   overrides.json (hand-checked topics), and the intermediate
                   segments.json / solutions.json / tags.json
    tools/mat/     the pipeline that generates all of the above

**Regenerating** (needs Python with PyMuPDF — `pip install pymupdf`):

    cd tools/mat
    python fetch.py       # download the source PDFs (skips what it already has)
    python segment.py     # split each paper into questions
    python solutions.py   # locate each question's official solution
    python render.py      # crop the question and solution images
    python tag.py         # auto-tag topics, then apply mat/data/overrides.json
    python build_db.py    # write questions.json + questions.js
    python make_page.py   # wrap bodies/mat-database.html in the site shell

**Adding next year's paper**: add a row to `tools/mat/manifest.py`, then re-run
the pipeline. Only 2018 needs special handling — its question pages carry no text
layer, so its layout is pinned by hand in `segment.py` (`MAP_2018`).

**Fixing a topic tag**: edit `mat/data/overrides.json` and re-run `tag.py` and
`build_db.py`. Topic ids are listed in `tools/mat/taxonomy.py`. Or use the
in-browser editor below, which writes the same file.

### Editing tags from the browser
The **Editor** button on the database page asks for a password, then puts an
*Edit tags* control on every question. Picking topics stages changes locally;
**Publish to GitHub** commits `mat/data/overrides.json` straight to this repo,
and everyone sees the new tags once the site redeploys.

The page reads `overrides.json` at load and layers it over the tags baked into
`questions.js`, so a published edit takes effect on the next deploy **without**
re-running the Python pipeline. Both paths read the same file, so the two stay
in step; re-running `tag.py` + `build_db.py` simply bakes the current overrides
back in.

Two things to be clear about, because this is a static site with no backend:

- **The password is not a security control.** It is checked in the browser and
  held as a digest (`PW_DIGEST` in `bodies/mat-database.html`), so the plaintext
  is not in the repo — but anyone can read the code and bypass the gate. That is
  acceptable, because unlocking on its own changes nothing anyone else can see.
  To change it, run the page's own `cyrb53` helper over the new password with
  seed `PW_SEED`, put the result in `PW_DIGEST`, and re-run `make_page.py`.
- **Publishing is what is actually protected.** It needs a GitHub personal
  access token with `Contents: write` on this repo, which you paste at publish
  time. It is sent only to `api.github.com` and is never written into the
  repository. You may optionally keep it in the browser's `localStorage` — only
  do that on a device you control, and revoke the token if you lose the device.

If you would rather not use a token at all, **Download overrides.json** saves
the updated file for you to commit by hand.

The MAT papers, solutions and examiner reports remain the copyright of the
University of Oxford and are mirrored here for educational use, with every entry
linking back to the official source.

## Deploying (pick one — all free)
**Vercel** (you already use it for Placing Jade News): `vercel deploy` from this
folder, or drag-and-drop the folder at vercel.com/new.
**GitHub Pages**: push this folder to a repo, Settings → Pages → deploy from branch.
**Netlify**: drag-and-drop the folder at app.netlify.com/drop.

## Editing
Each page's content lives between the <main> tags. Maths is written in LaTeX:
inline \( ... \), display \[ ... \] or $$ ... $$. The source bodies and the
build script (build.py, which injects the shared sidebar/header/footer) are in
the accompanying source folder if you prefer regenerating pages over editing
them directly.
