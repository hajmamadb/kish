# -*- coding: utf-8 -*-
# fetch_images3.py — مرحلهٔ سوم: ۱۸ مورد باقی‌مانده/ضعیف
import json, os, re, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "تصاویر")
os.makedirs(OUTDIR, exist_ok=True)
UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"
ENW = "https://en.wikipedia.org/w/api.php"

P = {
1:  [("commons", "Exploratorium San Francisco"), ("wiki", "Exploratorium")],
4:  [("commons", "teamLab Borderless"), ("wiki", "teamLab")],
6:  [("commons", "MUSA underwater museum"), ("commons", "underwater sculpture sea")],
7:  [("commons", "Royal Observatory Greenwich"), ("wiki", "Old Royal Observatory")],
8:  [("commons", "Fab Lab"), ("wiki", "Fab Lab")],
11: [("commons", "children robotics"), ("commons", "kids programming robots")],
14: [("commons", "Ithra"), ("wiki", "King Abdulaziz Center for World Culture")],
18: [("commons", "Arabic calligraphy"), ("commons", "calligraphy")],
21: [("commons", "Elbphilharmonie"), ("wiki", "Elbphilharmonie")],
22: [("commons", "theatre curtain stage performance"), ("commons", "theater stage lights")],
35: [("commons", "English classroom"), ("commons", "language classroom")],
39: [("commons", "community college classroom"), ("commons", "adult learning class")],
48: [("commons", "Kish lake"), ("commons", "wetland birds")],
49: [("commons", "Mad Science"), ("commons", "science show children")],
56: [("commons", "tourist information centre"), ("commons", "visitor centre information")],
59: [("commons", "Dubai Marina"), ("commons", "marina yachts")],
60: [("commons", "Dubai Fountain"), ("wiki", "Dubai Fountain")],
61: [("commons", "Kish film festival"), ("commons", "film festival cinema")],
}

def call(base, params, retries=6):
    url = base + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(min(int(e.headers.get("Retry-After", "10") or 10), 30) + 2)
                continue
            raise
    return None

def wiki_image(title):
    d = call(ENW, {"action": "query", "format": "json", "redirects": 1, "titles": title,
                   "prop": "pageimages", "piprop": "thumbnail|original", "pithumbsize": 1920})
    for p in d.get("query", {}).get("pages", {}).values():
        if "missing" in p:
            return None
        t = p.get("thumbnail", {})
        o = p.get("original", {})
        url = t.get("source") or o.get("source")
        return {"title": p.get("title"), "url": url, "w": t.get("width", o.get("width", 0))} if url else None
    return None

def commons_image(kw, limit=8):
    d = call(API, {"action": "query", "format": "json", "generator": "search",
                   "gsrsearch": 'filetype:bitmap "%s"' % kw, "gsrnamespace": 6, "gsrlimit": limit,
                   "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": 1920})
    out = []
    for p in d.get("query", {}).get("pages", {}).values():
        ii = p.get("imageinfo")
        if not ii:
            continue
        o = ii[0]
        if o.get("mime") not in ("image/jpeg", "image/png"):
            continue
        out.append({"title": p["title"], "w": o.get("width", 0),
                    "url": o.get("thumburl") if o.get("width", 0) > 1920 else o.get("url")})
    out.sort(key=lambda x: -x["w"])
    return out

def download(url, path):
    for attempt in range(4):
        try:
            req = urllib.request.Request(url, headers=UA)
            data = urllib.request.urlopen(req, timeout=120).read()
            if len(data) < 40000:
                return False
            with open(path, "wb") as fh:
                fh.write(data)
            return True
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(12)
                continue
            raise

cats = []
for f in ["part1.json", "part2.json", "part3a.json", "part3b.json"]:
    with open(os.path.join(HERE, f), encoding="utf-8") as fh:
        cats.extend(json.load(fh)["categories"])
title_of = {it["n"]: it["title"] for c in cats for it in c["items"]}

log = []
for n in sorted(P):
    safe = re.sub(r"[\\/:*?\"<>|]", " ", title_of[n]).strip()
    fn = "%02d_%s.jpg" % (n, safe)
    path = os.path.join(OUTDIR, fn)
    done, used = False, None
    for src, q in P[n]:
        try:
            time.sleep(1.5)
            cands = [wiki_image(q)] if src == "wiki" else commons_image(q)
            cands = [c for c in cands if c]
            if not cands:
                continue
            info = next((c for c in cands if c["w"] >= 900), cands[0])
            if download(info["url"], path):
                done = True
                used = (src + ":" + q, info["title"], info["w"])
                break
        except Exception as e:
            log.append({"n": n, "src": src, "q": q, "error": str(e)[:150]})
            continue
    log.append({"n": n, "ok": done, "src_q": used[0] if used else None,
                "file_used": used[1] if used else None, "width": used[2] if used else None,
                "path": fn, "bytes": os.path.getsize(path) if os.path.exists(path) else 0})
    print(("OK   " if done else "FAIL ") + str(n), (used[0] if used else ""), (used[1] if used else ""), flush=True)

ok = sum(1 for x in log if x.get("ok"))
print("\nTOTAL ok:", ok, "/", len(P))
with open(os.path.join(HERE, "fetch_log3.json"), "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
