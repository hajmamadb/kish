# -*- coding: utf-8 -*-
import hashlib, urllib.parse, urllib.request

UA = {"User-Agent": "KishComplexResearch/1.0 (educational research; contact: research@example.com)"}

def test(fn, label):
    h = hashlib.md5(fn.encode("utf-8")).hexdigest()
    d = h[:2]
    q = urllib.parse.quote(fn)
    url = "https://upload.wikimedia.org/wikipedia/commons/%s/%s/%s" % (d[0], d, q)
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=30)
        data = r.read(50000)
        print("%-12s OK  %s  %s" % (label, len(data), url))
    except Exception as e:
        print("%-12s FAIL %s  %s" % (label, str(e)[:60], url))

# فایل که قبلا با موفقیت دانلود شد (مورد ۵۵)
test("Dubai Mall, 2013 (Ank Kumar) 04.jpg", "known-good")
# فایل مورد ۶
test("The Dream Collector (22343585365).jpg", "item6")
# فایل مورد ۱۱
test("Iranian students robocup.jpg", "item11")
