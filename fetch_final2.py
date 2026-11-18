# -*- coding: utf-8 -*-
# fetch_final2.py — دانلود دو تصویر نهایی از Wayback (با Save-Page-Now اگر لازم شد)
import hashlib, json, os, re, time, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
UA = {"User-Agent": "KishResearch/1.0 (educational research; contact: research@example.com)"}
OUTDIR = os.path.join(HERE, "تصاویر")

def upload_url(fn, width=None):
    h = hashlib.md5(fn.encode("utf-8")).hexdigest()
    d = h[:2]
    q = urllib.parse.quote(fn)
    if width:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%dpx-%s" % (d[0], d, q, width, q)
    return "https://upload.wikimedia.org/wikipedia/commons/%s/%s/%s" % (d[0], d, q)

def avail(url):
    u = "https://archive.org/wayback/available?url=" + urllib.parse.quote(url, safe="")
    req = urllib.request.Request(u, headers=UA)
    d = json.load(urllib.request.urlopen(req, timeout=30))
    return d.get("archived_snapshots", {}).get("closest")

def save_page_now(url):
    u = "https://web.archive.org/save/" + url
    req = urllib.request.Request(u, headers=UA)
    try:
        r = urllib.request.urlopen(req, timeout=120)
        return r.status
    except urllib.error.HTTPError as e:
        return e.code

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

targets = [
    (6, "The Dream Collector (22343585365).jpg"),
    (11, "Iranian students robocup.jpg"),
]

for n, fn in targets:
    safe = re.sub(r"[\\/:*?\"<>|]", " ", title_of[n]).strip()
    path = os.path.join(OUTDIR, "%02d_%s.jpg" % (n, safe))
    url = upload_url(fn)
    try:
        snap = avail(url)
        if not snap:
            print("n=%d no snapshot, saving page now: %s" % (n, url), flush=True)
            code = save_page_now(url)
            print("  SPN status:", code, flush=True)
            for i in range(18):
                time.sleep(10)
                snap = avail(url)
                if snap:
                    break
        if snap:
            ts = snap["timestamp"]
            way = "https://web.archive.org/web/%sid_/%s" % (ts, url)
            sz = fetch(way, path)
            print("OK n=%d: %s (%d bytes) snap=%s" % (n, path, sz, ts), flush=True)
        else:
            print("FAIL n=%d: no snapshot available" % n, flush=True)
    except Exception as e:
        print("FAIL n=%d: %s" % (n, str(e)[:120]), flush=True)
print("done")
