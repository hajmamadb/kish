# -*- coding: utf-8 -*-
# fetch_images4.py — مرحلهٔ چهارم: ۱۲ مورد باقی‌مانده (wiki + دستهٔ Commons + جستجوی اصلاح‌شده)
import json, os, re, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "تصاویر")
os.makedirs(OUTDIR, exist_ok=True)
UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"
ENW = "https://en.wikipedia.org/w/api.php"

# n: [(منبع, پرس‌وجو), ...] — منبع: wiki | commons | cat (دسته)
P = {
6:  [("cat", "Underwater sculpture"), ("wiki", "MUSA (underwater museum)"), ("commons", "MUSA Quintana Roo")],
11: [("commons", "kids building robots"), ("commons", "robotics classroom")],
14: [("wiki", "King Abdulaziz Center for World Culture"), ("commons", "Ithra art museum")],
18: [("commons", "Islamic calligraphy"), ("commons", "calligraphy mosque")],
21: [("wiki", "Elbphilharmonie"), ("commons", "Elbphilharmonie interior")],
22: [("commons", "theatre seats red stage"), ("commons", "stage curtain theater")],
39: [("commons", "university lecture hall"), ("commons", "open university class")],
48: [("cat", "Kish Island"), ("commons", "Kish island lake")],
49: [("commons", "science show"), ("commons", "Mad Science Canada")],
56: [("cat", "Tourist information"), ("commons", "tourist office")],
60: [("cat", "Dubai Fountain"), ("wiki", "Dubai Fountain")],
61: [("wiki", "International Film Festival Rotterdam"), ("wiki", "Cannes Film Festival")],
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

def _parse(d):
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

def commons_image(kw, limit=8):
    d = call(API, {"action": "query", "format": "json", "generator": "search",
                   "gsrsearch": 'filetype:bitmap "%s"' % kw, "gsrnamespace": 6, "gsrlimit": limit,
                   "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": 1920})
    return _parse(d) if d else []

def cat_image(cat, limit=25, prefer=()):
    d = call(API, {"action": "query", "format": "json", "generator": "categorymembers",
                   "gcmtitle": "Category:%s" % cat, "gcmlimit": limit, "gcmtype": "file",
                   "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": 1920})
    cands = _parse(d) if d else []
    if prefer and cands:
        pref = [c for c in cands if any(k.lower() in c["title"].lower() for k in prefer)]
        if pref:
            return pref
    return cands

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
            if src == "wiki":
                cands = [wiki_image(q)]
            elif src == "cat":
                prefer = {"Kish Island": ("lake", "hing", "bird", "wetland"),
                          }.get(q, ())
                cands = cat_image(q, prefer=prefer)
            else:
                cands = commons_image(q)
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
with open(os.path.join(HERE, "fetch_log4.json"), "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
