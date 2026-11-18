# -*- coding: utf-8 -*-
# fetch_direct.py — دانلود مستقیم از upload.wikimedia.org با نام‌فایل دقیق (بدون API)
import hashlib, os, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}
OUTDIR = os.path.join(HERE, "تصاویر")

def upload_url(fn, width=None):
    h = hashlib.md5(fn.encode("utf-8")).hexdigest()
    d = h[:2]
    q = urllib.parse.quote(fn)
    if width:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%dpx-%s" % (d[0], d, q, width, q)
    return "https://upload.wikimedia.org/wikipedia/commons/%s/%s/%s" % (d[0], d, q)

def download(url, path):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=90).read()
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)

jobs = [
    (6, "06_موزه هنر زیرآبی (با تور غواصی).jpg", "The Dream Collector (22343585365).jpg"),
    (11, "11_مدرسه STEM، کدنویسی و رباتیک کودکان.jpg", "Iranian students robocup.jpg"),
]

for n, local, fn in jobs:
    path = os.path.join(OUTDIR, local)
    try:
        url = upload_url(fn, 1920)
        try:
            sz = download(url, path)
        except urllib.error.HTTPError as e:
            if e.code in (400, 404):
                url = upload_url(fn)  # بدون تامبنیل
                sz = download(url, path)
            else:
                raise
        print("OK n=%d: %s (%d bytes)" % (n, local, sz))
    except Exception as e:
        print("FAIL n=%d: %s" % (n, str(e)[:120]))
print("done")
