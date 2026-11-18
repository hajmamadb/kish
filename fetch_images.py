# -*- coding: utf-8 -*-
# fetch_images.py v2 — عکس واقعی هر ۶۱ مورد از Wikimedia Commons (با مدیریت rate-limit)
import json, os, re, time, urllib.request, urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, "تصاویر")
os.makedirs(OUTDIR, exist_ok=True)
UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}
API = "https://commons.wikimedia.org/w/api.php"

K = {
1:  ["Exploratorium San Francisco"],
2:  ["Cité des enfants"],
3:  ["La Géode Paris"],
4:  ["teamLab Borderless"],
5:  ["Dubai Aquarium"],
6:  ["MUSA underwater museum"],
7:  ["Old Royal Observatory Greenwich"],
8:  ["Fab Lab"],
9:  ["virtual reality headset person"],
10: ["science cafe"],
11: ["kids robotics classroom"],
12: ["Kennedy Space Center Visitor Complex"],
13: ["Persian Gulf coral reef"],
14: ["Ithra King Abdulaziz Center for World Culture"],
15: ["Kish Island"],
16: ["Kish archaeology"],
17: ["potter wheel pottery workshop"],
18: ["Persian calligraphy"],
19: ["Stadtbibliothek Stuttgart"],
20: ["ancient Greek theatre Delphi"],
21: ["Elbphilharmonie Hamburg"],
22: ["black box theatre"],
23: ["IMAX screen"],
24: ["Louvre at night"],
25: ["night market street food"],
26: ["Hosier Lane Melbourne"],
27: ["puppet theatre"],
28: ["book cafe"],
29: ["newsroom television"],
30: ["Pinewood Studios"],
31: ["radio studio microphone"],
32: ["Museum of the Moving Image"],
33: ["press conference journalists"],
34: ["esports arena"],
35: ["language classroom students"],
36: ["university campus"],
37: ["Moscow Congress Center"],
38: ["painting restoration studio"],
39: ["adult education classroom"],
40: ["KidZania"],
41: ["escape room"],
42: ["immersive theatre"],
43: ["Singapore Flyer"],
44: ["open-air cinema"],
45: ["Bosco Verticale Milan"],
46: ["padel court"],
47: ["Saras hot springs Kish"],
48: ["Hing lake Kish"],
49: ["Mad Science"],
50: ["Mercato Centrale Florence"],
51: ["WeWork office"],
52: ["rooftop restaurant city view"],
53: ["boutique hotel interior"],
54: ["museum gift shop"],
55: ["Dubai Mall"],
56: ["tourist information office"],
57: ["Federation Square Melbourne"],
58: ["Dubai Marina promenade"],
59: ["Dubai Marina yachts"],
60: ["Dubai Fountain"],
61: ["Kish International Short Film Festival"],
}

def api(params, retries=5):
    url = API + "?" + urllib.parse.urlencode(params)
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=UA)
            return json.load(urllib.request.urlopen(req, timeout=60))
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                wait = int(e.headers.get("Retry-After", "10") or 10)
                wait = min(wait, 30)
                time.sleep(wait + 1)
                continue
            raise
    return None

def search_files(kw, limit=6):
    # یک فراخوانی واحد: search به‌عنوان generator + imageinfo
    d = api({"action": "query", "format": "json", "generator": "search",
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
                    "thumb": o.get("thumburl"), "url": o.get("url")})
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
for n in sorted(K):
    safe = re.sub(r"[\\/:*?\"<>|]", " ", title_of[n]).strip()
    fn = "%02d_%s.jpg" % (n, safe)
    path = os.path.join(OUTDIR, fn)
    if os.path.exists(path) and os.path.getsize(path) > 40000:
        log.append({"n": n, "ok": True, "skip": True, "path": fn})
        print("SKIP " + str(n) + " (already ok)", flush=True)
        continue
    done, used = False, None
    for kw in K[n]:
        try:
            time.sleep(1.2)
            infos = search_files(kw)
            if not infos:
                continue
            infos.sort(key=lambda x: -x["w"])
            info = next((i for i in infos if i["w"] >= 1200), infos[0])
            dl = info["thumb"] if info["w"] > 1920 else info["url"]
            if download(dl, path):
                done, used = True, (kw, info["title"], info["w"])
                break
        except Exception as e:
            log.append({"n": n, "kw": kw, "error": str(e)[:150]})
            continue
    log.append({"n": n, "ok": done, "kw_used": used[0] if used else None,
                "file_used": used[1] if used else None, "width": used[2] if used else None,
                "path": fn, "bytes": os.path.getsize(path) if os.path.exists(path) else 0})
    print(("OK   " if done else "FAIL ") + str(n), (used[1] if used else ""), flush=True)

ok = sum(1 for x in log if x.get("ok"))
print("\nTOTAL ok:", ok, "/", len(K))
with open(os.path.join(HERE, "fetch_log.json"), "w", encoding="utf-8") as fh:
    json.dump(log, fh, ensure_ascii=False, indent=1)
