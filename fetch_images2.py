# -*- coding: utf-8 -*-
# fetch_images2.py — مرحلهٔ دوم: تصحیح و تکمیل ۶۱ عکس
# منبع: (wiki) تصویر برتر مقالهٔ ویکی‌پدیای انگلیسی مکان / (commons) جستجوی Commons
import json, os, re, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "تصاویر")
os.makedirs(OUTDIR, exist_ok=True)
UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"
ENW = "https://en.wikipedia.org/w/api.php"

# مواردی که از مرحلهٔ اول درست هستند — دست نمی‌خورد
KEEP = {10, 12, 19, 23, 25, 26, 32, 34, 40, 41, 44, 46, 54, 55}

# n: [(منبع, پرس‌وجو), ...] به ترتیب اولویت
P = {
1:  [("wiki", "Exploratorium")],
2:  [("wiki", "Please Touch Museum"), ("commons", "children's science museum")],
3:  [("wiki", "La Géode"), ("commons", "La Géode")],
4:  [("wiki", "teamLab")],
5:  [("wiki", "Dubai Aquarium and Underwater Zoo"), ("wiki", "Monterey Bay Aquarium")],
6:  [("wiki", "MUSA (underwater museum)"), ("commons", "underwater sculpture sea")],
7:  [("wiki", "Old Royal Observatory")],
8:  [("wiki", "Fab Lab")],
9:  [("commons", "virtual reality headset"), ("commons", "VR person using")],
11: [("commons", "kids robotics"), ("commons", "children programming class")],
13: [("commons", "coral reef"), ("commons", "coral reef underwater")],
14: [("wiki", "King Abdulaziz Center for World Culture")],
15: [("wiki", "Kish Island")],
16: [("commons", "Kish island archaeology"), ("commons", "Dilmun")],
17: [("commons", "potter wheel"), ("commons", "pottery workshop")],
18: [("commons", "Persian calligraphy"), ("commons", "calligraphy")],
20: [("wiki", "Theatre of Delphi")],
21: [("wiki", "Elbphilharmonie")],
22: [("commons", "theatre stage"), ("wiki", "Black box theatre")],
24: [("commons", "Louvre at night"), ("wiki", "Musée du Louvre")],
27: [("commons", "wayang kulit"), ("commons", "puppet show")],
28: [("commons", "bookshop interior"), ("commons", "bookstore")],
29: [("commons", "newsroom"), ("commons", "news studio anchor")],
30: [("wiki", "Pinewood Studios"), ("commons", "film studio lot")],
31: [("commons", "radio studio"), ("commons", "broadcast studio")],
33: [("commons", "press conference"), ("commons", "conference journalists")],
35: [("commons", "classroom students"), ("commons", "language class")],
36: [("wiki", "Massachusetts Institute of Technology"), ("commons", "university campus")],
37: [("wiki", "Moscow Congress Center"), ("commons", "convention center")],
38: [("commons", "painting restoration"), ("commons", "art restorer")],
39: [("commons", "adult education class"), ("commons", "senior learning classroom")],
42: [("wiki", "Sleep No More (play)"), ("commons", "immersive theatre")],
43: [("wiki", "Singapore Flyer")],
45: [("wiki", "Bosco Verticale")],
47: [("commons", "Saras Kish"), ("commons", "hot springs pool")],
48: [("commons", "Hing lake Kish"), ("commons", "wetland birds lake")],
49: [("wiki", "Mad Science"), ("commons", "science show children")],
50: [("wiki", "Mercato Centrale"), ("commons", "food hall")],
51: [("wiki", "WeWork"), ("commons", "coworking space")],
52: [("commons", "rooftop restaurant"), ("commons", "rooftop bar city view")],
53: [("commons", "boutique hotel"), ("commons", "design hotel room")],
56: [("commons", "tourist information"), ("commons", "tourist office")],
57: [("wiki", "Federation Square")],
58: [("wiki", "Dubai Marina")],
59: [("wiki", "Dubai Maritime City"), ("commons", "marina yachts")],
60: [("wiki", "Dubai Fountain")],
61: [("commons", "Kish film festival"), ("wiki", "International Film Festival Rotterdam")],
}

def call(base, params, retries=5):
    url = base + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(min(int(e.headers.get("Retry-After", "10") or 10), 30) + 1)
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

def commons_image(kw, limit=6):
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
    if n in KEEP:
        log.append({"n": n, "ok": True, "kept": True, "path": fn})
        continue
    done, used = False, None
    for src, q in P[n]:
        try:
            time.sleep(1.2)
            if src == "wiki":
                info = wiki_image(q)
                cands = [info] if info else []
            else:
                cands = commons_image(q)
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
print("\nTOTAL ok:", ok, "/", (len(P) + len(KEEP)))
with open(os.path.join(HERE, "fetch_log2.json"), "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
