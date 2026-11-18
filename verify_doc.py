# -*- coding: utf-8 -*-
import zipfile, re, os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
f = "مجتمع_کیش_فهرست_امکانات.docx"
print("size KB:", round(os.path.getsize(f) / 1024, 1))
xml = zipfile.ZipFile(f).read("word/document.xml").decode("utf-8")
paras = re.findall(r"<w:p[ >].*?</w:p>", xml, re.S)
texts = []
for p in paras:
    t = "".join(re.findall(r"<w:t[^>]*>(.*?)</w:t>", p, re.S))
    if t.strip():
        texts.append(t)
print("non-empty paragraphs:", len(texts))
# checks
checks = {
    "title page": "جزیرهٔ کیش" in texts[0],
    "sec1": any(t.startswith("بخش ۱") for t in texts),
    "sec2": any(t.startswith("بخش ۲") for t in texts),
    "sec3": any(t.startswith("بخش ۳") for t in texts),
    "sec4": any(t.startswith("بخش ۴") for t in texts),
    "sec5": any(t.startswith("بخش ۵") for t in texts),
    "item1": any(t.startswith("۱. ") for t in texts),
    "item61": any(t.startswith("۶۱. ") for t in texts),
    "user item51": any("۵۱." in t and "کوورک" in t for t in texts),
    "cat7": any("ز) گردشگری" in t for t in texts),
    "legend ok": any("✅" in t for t in texts),
    "legend warn": any("⚠️" in t for t in texts),
}
for k, v in checks.items():
    print(("PASS " if v else "FAIL ") + k)
# count item headings
items = [t for t in texts if re.match(r"^\d{1,2}\. ", t) or re.match(r"^[۰-۹]{1,2}\. ", t)]
print("item heading count:", len(items))
# show first 12 and last 8 non-empty paragraphs as sample
print("\n--- first 12 paragraphs ---")
for t in texts[:12]:
    print(t[:100])
print("\n--- last 8 paragraphs ---")
for t in texts[-8:]:
    print(t[:100])
