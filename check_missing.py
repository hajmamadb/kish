# -*- coding: utf-8 -*-
import os, time, urllib.request, json
os.chdir(os.path.dirname(os.path.abspath(__file__)))
d = os.listdir("تصاویر")
nums = sorted(int(f[:2]) for f in d if f[:2].isdigit() and f[2:3] == "_")
missing = [n for n in range(1, 62) if n not in nums]
print("image count:", len(d))
print("missing:", missing)
for f in d:
    if f[:2] in ("06", "11", "39", "56"):
        print(f, os.path.getsize(f))
t0 = time.time()
try:
    url = ("https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search"
           "&srsearch=filetype:bitmap%20MUSA&srnamespace=6&srlimit=3")
    req = urllib.request.Request(url, headers={"User-Agent": "KishResearch/1.0"})
    r = json.load(urllib.request.urlopen(req, timeout=20))
    print("commons OK %.1fs:" % (time.time() - t0), [x["title"] for x in r["query"]["search"]])
except Exception as e:
    print("commons FAIL %.1fs:" % (time.time() - t0), e)
