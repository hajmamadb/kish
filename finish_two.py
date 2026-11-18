# -*- coding: utf-8 -*-
# finish_two.py — بررسی/دریافت دو تصویر باقی‌مانده از Wayback
import hashlib, json, os, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
UA = {"User-Agent": "KishResearch/1.0 (educational research; contact: research@example.com)"}
OUTDIR = os.path.join(HERE, "تصاویر")

def upload_url(fn):
    h = hashlib.md5(fn.encode("utf-8")).hexdigest()
    d = h[:2]
    return "https://upload.wikimedia.org/wikipedia/commons/%s/%s/%s" % (d[0], d, urllib.parse.quote(fn))

def avail(url):
    u = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    req = urllib.request.Request(u, headers=UA)
    d = json.load(urllib.request.urlopen(req, timeout=30))
    return d.get("archived_snapshots", {}).get("closest")

def fetch(url, path, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=timeout).read()
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)

cats = []
for f in ["part1.json", "part2.json", "part3a.json", "part3b.json"]:
    with open(f, encoding="utf-8") as fh:
        cats.extend(json.load(fh)["categories"])
title_of = {it["n"]: it["title"] for c in cats for it in c["items"]}

targets = [(6, "The Dream Collector (22343585365).jpg"), (11, "Iranian students robocup.jpg")]
for n, fn in targets:
    safe = re.sub(r"[\\/:*?\"<>|]", " ", title_of[n]).strip()
    path = os.path.join(OUTDIR, "%02d_%s.jpg" % (n, safe))
    if os.path.exists(path) and os.path.getsize(path) > 40000:
        print("n=%d already ok (%d bytes)" % (n, os.path.getsize(path)))
        continue
    url = upload_url(fn)
    snap = avail(url)
    if snap:
        ts = snap["timestamp"]
        way = "https://web.archive.org/web/%sid_/%s" % (ts, url)
        try:
            sz = fetch(way, path)
            print("OK n=%d: %d bytes (snap %s)" % (n, sz, ts))
        except Exception as e:
            print("FAIL n=%d fetch: %s" % (n, str(e)[:100]))
    else:
        print("n=%d: NO snapshot yet for %s" % (n, url))

# وضعیت کلی پوشه
files = os.listdir(OUTDIR)
nums = sorted(int(f[:2]) for f in files if f[:2].isdigit() and f[2:3] == "_")
print("total images:", len(files), "| missing:", [i for i in range(1, 62) if i not in nums])
