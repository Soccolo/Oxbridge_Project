import os, sys, time, urllib.request
sys.path.insert(0, os.path.dirname(__file__))
from manifest import PAPERS, SYLLABUS
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "mat", "papers")
UA = {"User-Agent": "Mozilla/5.0 (educational archive fetch)"}
jobs = [("syllabus.pdf", SYLLABUS)]
for pid, label, test, sol, fb in PAPERS:
    jobs.append((f"{pid}-paper.pdf", test))
    if sol: jobs.append((f"{pid}-solutions.pdf", sol))
    if fb:  jobs.append((f"{pid}-feedback.pdf", fb))
ok = fail = skip = 0
for name, url in jobs:
    dest = os.path.join(OUT, name)
    if os.path.exists(dest) and os.path.getsize(dest) > 1000:
        skip += 1; continue
    try:
        req = urllib.request.Request(url, headers=UA)
        data = urllib.request.urlopen(req, timeout=60).read()
        if not data.startswith(b"%PDF"):
            print(f"  NOT-PDF {name}"); fail += 1; continue
        open(dest, "wb").write(data)
        print(f"  ok {name:24s} {len(data)//1024:5d} KB"); ok += 1
        time.sleep(0.4)
    except Exception as e:
        print(f"  FAIL {name}: {e}"); fail += 1
print(f"\ndownloaded={ok} skipped={skip} failed={fail} total_jobs={len(jobs)}")
