# -*- coding: utf-8 -*-
# fetch_final.py — دو مورد نهایی با روش MD5 + upload.wikimedia.org
import hashlib, json, os, re, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}
OUTDIR = os.path.join(HERE, "تصاویر")

def commons_url(filename, width=1600):
    h = hashlib.md5(filename.encode("utf-8")).hexdigest()
    d = h[:2]
    quoted = urllib.parse.quote(filename)
    if width:
        return "https://upload.wikimedia.org/wikipedia/commons/thumb/%s/%s/%s/%dpx-%s" % (d[0], d, quoted, width, quoted)
    return "https://upload.wikimedia.org/wikipedia/commons/%s/%s/%s" % (d[0], d, quoted)

def download(url, path):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=90).read()
    with open(path, "wb") as fh:
        fh.write(data)
    return len(data)

cats = []
for f in ["part1.json", "part2.json", "part3a.json", "part3b.json"]:
    with open(f, encoding="utf-8") as fh:
        cats.extend(json.load(fh)["categories"])
title_of = {it["n"]: it["title"] for c in cats for it in c["items"]}

# مورد ۶: موزه هنر زیرآبی — مجسمهٔ معروف «The Dream Collector» از MUSA (کانکون)
fn6 = "The Dream Collector (22343585365).jpg"
safe6 = re.sub(r"[\\/:*?\"<>|]", " ", title_of[6]).strip()
p6 = os.path.join(OUTDIR, "06_%s.jpg" % safe6)
try:
    u6 = commons_url(fn6, 1920)
    sz = download(u6, p6)
    print("OK 6:", p6, sz, "bytes <-", fn6)
except Exception as e:
    print("FAIL 6:", e)
