# -*- coding: utf-8 -*-
import json, os, re, time, urllib.request, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"
ENW = "https://en.wikipedia.org/w/api.php"
OUTDIR = os.path.join(HERE, "تصاویر")

P = {
6:  [("commons", "MUSA"), ("commons", "underwater museum"), ("wiki", "Underwater sculpture"),
     ("commons", "scuba diver statue underwater")],
11: [("commons", "ROBOCUP junior"), ("commons", "young people robots"),
     ("commons", "school robotics"), ("wiki", "Robotics")],
}

def call(base, params, retries=4):
    url = base + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=25))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(15)
                continue
            raise
    return None

def wiki_image(title):
    d = call(ENW, {"action": "query", "format": "json", "redirects": 1, "titles": title,
                   "prop": "pageimages", "piprop": "thumbnail|original", "pithumbsize": 1920})
    for p in d.get("query", {}).get("pages", {}).values():
        if "missing" in p:
            return None
        t, o = p.get("thumbnail", {}), p.get("original", {})
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

def commons_image(kw, limit=10, minw=800):
    d = call(API, {"action": "query", "format": "json", "generator": "search",
                   "gsrsearch": 'filetype:bitmap "%s"' % kw, "srnamespace": 6, "srlimit": limit,
                   "prop": "imageinfo", "iiprop": "url|size|mime", "iiurlwidth": 1920})
    return [c for c in _parse(d) if c["w"] >= minw] if d else []

def download(url, path):
    req = urllib.request.Request(url, headers=UA)
    data = urllib.request.urlopen(req, timeout=60).read()
    if len(data) < 40000:
        return False
    with open(path, "wb") as fh:
        fh.write(data)
    return True

cats = []
for f in ["part1.json", "part2.json", "part3a.json", "part3b.json"]:
    with open(f, encoding="utf-8") as fh:
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
            time.sleep(2)
            cands = [wiki_image(q)] if src == "wiki" else commons_image(q)
            cands = [c for c in cands if c]
            if not cands:
                continue
            info = cands[0]
            if download(info["url"], path):
                done = True
                used = (src + ":" + q, info["title"], info["w"])
                break
        except Exception as e:
            log.append({"n": n, "src": src, "q": q, "error": str(e)[:150]})
    log.append({"n": n, "ok": done, "src_q": used[0] if used else None,
                "file_used": used[1] if used else None, "width": used[2] if used else None})
    print(("OK   " if done else "FAIL ") + str(n), (used[0] if used else ""), (used[1] if used else ""), flush=True)

with open("fetch_log7.json", "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
print("done")
