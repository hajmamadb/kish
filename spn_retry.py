# -*- coding: utf-8 -*-
# spn_retry.py — تلاش مجدد Save-Page-Now برای ۴ فایل
import hashlib, json, os, time, urllib.parse, urllib.request

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

def spn(url):
    req = urllib.request.Request("https://web.archive.org/save/" + url, headers=UA)
    try:
        r = urllib.request.urlopen(req, timeout=120)
        return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception as e:
        return str(e)[:60]

def fetch(url, path, timeout=120):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=timeout).read()
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)

files = {
    6: "The Dream Collector (22343585365).jpg",
    11: "Iranian students robocup.jpg",
    39: "Classroom @ university.jpg",
    48: "Gazella subgutturosa in Kish Island2020-03-30 12.jpg",
}

for n, fn in files.items():
    url = upload_url(fn)
    code = spn(url)
    print("n=%d SPN -> %s" % (n, code), flush=True)
    snap = None
    if code == 200 or code == 302:
        for i in range(12):
            time.sleep(10)
            snap = avail(url)
            if snap:
                break
    if snap:
        ts = snap["timestamp"]
        sz = fetch("https://web.archive.org/web/%sid_/%s" % (ts, url), os.path.join(OUTDIR, "tmp_%d" % n))
        print("n=%d OK: %d bytes (snap %s)" % (n, sz, ts), flush=True)
    else:
        print("n=%d: still no snapshot" % n, flush=True)
    time.sleep(5)
print("done")
