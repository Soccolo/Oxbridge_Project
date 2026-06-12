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
- styles.css

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
