# -*- coding: utf-8 -*-
import time, urllib.request

tests = [
    ("https://example.com/", "example"),
    ("https://en.wikipedia.org/wiki/Kish_Island", "wikipedia"),
    ("https://commons.wikimedia.org/w/api.php?action=query&format=json&list=search&srsearch=filetype:bitmap%20MUSA&srnamespace=6&srlimit=2", "commons-api"),
    ("https://upload.wikimedia.org/wikipedia/commons/thumb/0/0e/Dubai_Mall_2013.jpg/1280px-Dubai_Mall_2013.jpg", "upload"),
]
for url, name in tests:
    t0 = time.time()
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "KishResearch/1.0"})
        data = urllib.request.urlopen(req, timeout=15).read()
        print("%-12s OK  %.1fs  %d bytes" % (name, time.time() - t0, len(data)))
    except Exception as e:
        print("%-12s FAIL %.1fs: %s" % (name, time.time() - t0, str(e)[:100]))
