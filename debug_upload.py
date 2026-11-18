# -*- coding: utf-8 -*-
import hashlib, urllib.parse, urllib.request

UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}
fn = "The Dream Collector (22343585365).jpg"
h = hashlib.md5(fn.encode("utf-8")).hexdigest()
d = h[:2]
quoted = urllib.parse.quote(fn)
urls = [
    ("original", "https://upload.wikimedia.org/wikipedia/commons/%s/%s/%s" % (d[0], d, quoted)),
    ("thumb-1920", "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/1920px-%s" % (d[0], d, quoted, quoted)),
    ("thumb-1280", "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/1280px-%s" % (d[0], d, quoted, quoted)),
    ("control", "https://upload.wikimedia.org/wikipedia/commons/0/0e/Dubai_Mall_2013.jpg"),
]
for name, url in urls:
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=30)
        data = r.read(200000)
        print(name, "OK", r.status, len(data), "bytes")
    except Exception as e:
        print(name, "FAIL", str(e)[:80])
