# -*- coding: utf-8 -*-
# fetch_wayback.py — دانلود فایل‌های دقیق از Wayback (اگر snapshot وجود داشته باشد)
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

def fetch(url, path, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=timeout).read()
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)

# n: [(filename, filename fallback, ...)]
PLAN = {
6:  ["The Dream Collector (22343585365).jpg", "Urban Reef (22330563812).jpg", "DSCN0585 (14292929642).jpg"],
11: ["Iranian students robocup.jpg", "Robocupjuniordance.jpg", "HTWK Leipzig - Nao-Team.jpg"],
39: ["Classroom @ university.jpg", "Biola University Lecture Hall.JPG", "Classroom in RCoE - 1.JPG"],
48: ["Gazella subgutturosa in Kish Island2020-03-30 12.jpg", "Kish island 02.jpg", "Kish Island2020-04-01 10.jpg"],
}

for n, files in PLAN.items():
    got = False
    for fn in files:
        url = upload_url(fn)
        try:
            snap = avail(url)
            if not snap:
                print("n=%d no snapshot: %s" % (n, fn))
                continue
            ts = snap["timestamp"]
            way = "https://web.archive.org/web/%sid_/%s" % (ts, url)
            sz = fetch(way, os.path.join(OUTDIR, "tmp_%d" % n))
            print("n=%d OK via wayback: %s (%d bytes, snap %s)" % (n, fn, sz, ts))
            got = True
            break
        except Exception as e:
            print("n=%d FAIL %s: %s" % (n, fn, str(e)[:90]))
            time.sleep(2)
    if not got:
        print("n=%d: NO WAYBACK SNAPSHOT for any candidate" % n)
print("done")
