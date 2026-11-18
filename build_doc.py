# -*- coding: utf-8 -*-
# build_doc.py — ساخت سند «فهرست امکانات مجتمع کیش»
import json, os
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "مجتمع_کیش_فهرست_امکانات.docx")

NAVY = RGBColor(0x1F, 0x4E, 0x79)
BLUE = RGBColor(0x2E, 0x53, 0x95)
DARK = RGBColor(0x21, 0x21, 0x21)
GRAY = RGBColor(0x59, 0x59, 0x59)
GREEN = RGBColor(0x1E, 0x7A, 0x1E)
AMBER = RGBColor(0xB3, 0x6B, 0x00)
FONT = "Tahoma"

def _rtl(r):
    rpr = r._element.get_or_add_rPr()
    rpr.append(OxmlElement("w:rtl"))

def _bidi(p):
    p._p.get_or_add_pPr().append(OxmlElement("w:bidi"))

def para(doc, text="", size=10, color=DARK, bold=False, italic=False,
         align=WD_ALIGN_PARAGRAPH.RIGHT, before=0, after=4, line=1.15):
    p = doc.add_paragraph()
    _bidi(p)
    p.alignment = align
    pf = p.paragraph_format
    pf.space_before = Pt(before)
    pf.space_after = Pt(after)
    pf.line_spacing = line
    if text:
        r = p.add_run(text)
        r.font.name = FONT
        r._element.rPr.rFonts.set(qn("w:cs"), FONT)
        r.font.size = Pt(size)
        r.font.color.rgb = color
        r.font.bold = bold
        r.font.italic = italic
        _rtl(r)
    return p

def run(p, text, size=10, color=DARK, bold=False, italic=False):
    r = p.add_run(text)
    r.font.name = FONT
    r._element.rPr.rFonts.set(qn("w:cs"), FONT)
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.bold = bold
    r.font.italic = italic
    _rtl(r)
    return r

def heading(doc, text, size=14, color=NAVY, before=14, after=6):
    return para(doc, text, size=size, color=color, bold=True, before=before, after=after)

def hline(doc):
    p = para(doc, "", after=2)
    pPr = p._p.get_or_add_pPr()
    pbdr = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "1F4E79")
    pbdr.append(bottom)
    pPr.append(pbdr)
    return p

FA = "۰۱۲۳۴۵۶۷۸۹"
def fa(n):
    return "".join(FA[int(c)] if c.isdigit() else c for c in str(n))

# ---------- بارگذاری داده‌ها ----------
cats = []
for f in ["part1.json", "part2.json", "part3a.json", "part3b.json"]:
    with open(os.path.join(HERE, f), encoding="utf-8") as fh:
        cats.extend(json.load(fh)["categories"])
titles = {it["n"]: it["title"] for c in cats for it in c["items"]}
total = sum(len(c["items"]) for c in cats)

doc = Document()
st = doc.styles["Normal"]
st.font.name = FONT
st.font.size = Pt(10)
st.element.get_or_add_rPr().rFonts.set(qn("w:cs"), FONT)
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21), Cm(29.7)
sec.left_margin = sec.right_margin = Cm(2.2)
sec.top_margin, sec.bottom_margin = Cm(2), Cm(2)

# ---------- صفحهٔ عنوان ----------
for _ in range(5):
    para(doc, "", after=10)
para(doc, "جزیرهٔ کیش", size=26, color=NAVY, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, after=6)
para(doc, "طرح مجتمع چندرشته‌ای علمی، فرهنگی، رسانه‌ای و تفریحی", size=14, color=BLUE, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=14)
para(doc, "فهرست امکانات، بخش‌ها و خدمات پیشنهادی", size=16, color=DARK, bold=True,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=4)
para(doc, "۷ دسته — %s مورد — هر مورد با نمونه‌های واقعی جهانی" % fa(total), size=11, color=GRAY,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=30)
para(doc, "تاریخ تدوین: ۱۵ آذر ۱۴۰۵ (۲۰۲۶/۱۱/۰۶)", size=10, color=GRAY,
     align=WD_ALIGN_PARAGRAPH.CENTER, after=0)
doc.add_page_break()

# ---------- بخش ۱: مقدمه ----------
heading(doc, "بخش ۱ — مقدمه و هدف سند", 14)
hline(doc)
para(doc, "این سند فهرست جامع «امکانات، بخش‌ها و خدمات» پیشنهادی برای مجتمع چندرشته‌ای کیش (ترکیب علمی، "
          "فرهنگی، رسانه‌ای، آموزشی، تفریحی، تجاری و گردشگری) است. فهرست هم برای ساکنان و هم برای گردشگران "
          "طراحی شده و فضاهای سرپوشیده (مناسب تابستان‌های گرم و مرطوب) و فضای باز (ساحل، بوم‌راه، سینمای روباز) را "
          "دربر می‌گیرد. در این مرحله هیچ محدودیت بودجه یا مساحت در نظر گرفته نشده است.", after=8)
para(doc, "هر مورد شامل: عنوان، توصیف ۱ تا ۳ خطی و ۱ تا ۵ نمونهٔ واقعی از سراسر جهان با حقایق کلیدی "
          "(شهر/کشور، سال، اعداد مهم) است. نمونه‌ها با علامت ✅ (تأییدشده از ویکی‌پدیای انگلیسی در تاریخ "
          "۲۰۲۶/۱۱/۰۶) یا ⚠️ (بر اساس دانش عمومی و قابل‌بررسی) علامت‌گذاری شده‌اند؛ جزئیات در بخش ۵.", after=10)

# ---------- بخش ۲: پروفایل کیش ----------
heading(doc, "بخش ۲ — پروفایل جزیرهٔ کیش (پیش‌زمینه)", 14)
hline(doc)
profile = [
    "سطح: ۹۱/۵ کیلومتر مربع — یکی از بزرگ‌ترین جزایر ایران؛ جمعیت دائمی حدود ۵۵٬۲۰۵ نفر (سرشماری ۱۳۹۵) در مقابل چند میلیون مسافر در سال.",
    "آب‌وهوا: تابستان‌های گرم و مرطوب و زمستان‌های ملایم و خشک — نیاز به ترکیب قوی فضاهای سرپوشیده با فضاهای ساحلی/شبانه.",
    "جاذبه‌های موجود: پارک دلفین‌ها، آکواریوم، Mica Mall (حدود ۱۹۵٬۰۰۰ مترمربع)، شهر زیرزمینی کاریز، شهر تاریخی حریره (قرن ۸)، کشتی یونانی (۱۹۴۳)، دریاچهٔ هینگه و باغ پرندگان، آبگرم سرارس، بازی‌های ساحلی.",
    "رویداد: فستیوال فیلم کوتاه بین‌المللی کیش از ۱۹۹۴ هر سال برگزار می‌شود — پایهٔ طبیعی برای «خانهٔ فستیوال‌ها».",
    "مزیت اقتصادی: منطقهٔ آزاد تجاری-صنعتی (معافیت‌های گمرکی و تعرفه‌ای) — مزیت رقابتی برای بخش‌های تجاری و رویداد.",
    "شهرهای خواهرخوانده: لانگکوی (مالزی)، دبی (امارات) و لاپو-لاپو (فیلیپین).",
]
for b in profile:
    p = para(doc, "", after=3)
    run(p, "• ", size=10, color=NAVY, bold=True)
    run(p, b, size=10)

# ---------- بخش ۳: فهرست ۶۱ مورد ----------
doc.add_page_break()
heading(doc, "بخش ۳ — فهرست %s مورد (۷ دسته)" % fa(total), 14)
hline(doc)
for c in cats:
    heading(doc, c["title"], 13, color=NAVY, before=12)
    if c.get("intro"):
        para(doc, c["intro"], size=10, color=GRAY, italic=True, after=6)
    for it in c["items"]:
        p = para(doc, "", before=8, after=2)
        run(p, "%s. " % fa(it["n"]), size=11.5, color=BLUE, bold=True)
        run(p, it["title"], size=11.5, color=BLUE, bold=True)
        para(doc, it["desc"], size=10, after=2)
        for ex in it["examples"]:
            p = para(doc, "", after=1, line=1.1)
            p.paragraph_format.left_indent = Cm(0.4)
            mark = "✅" if ex["v"] == "ok" else "⚠️"
            col = GREEN if ex["v"] == "ok" else AMBER
            run(p, "   • ", size=9.5, color=GRAY)
            run(p, ex["name"] + "  ", size=10, bold=True)
            run(p, "(" + ex["loc"] + ") — ", size=9.5, color=GRAY)
            run(p, ex["facts"], size=9.5, color=DARK)
            run(p, "  " + mark, size=9.5, color=col)

# ---------- بخش ۴: نگاشت مطالعات موردی پوشه ----------
doc.add_page_break()
heading(doc, "بخش ۴ — مطالعات موردی موجود در پوشه و نگاشت به این فهرست", 14)
hline(doc)
para(doc, "شش مطالعهٔ موردی آماده در همین پوشه هستند؛ ستون «نگاشت» نشان می‌دهد هر مطالعه با کدام موارد این "
          "فهرست همپوشانی دارد:", after=8)
CASES = [
    ("Barbican Centre (لندن، انگلستان)", [19, 21, 22, 23, 45, 39]),
    ("Cité des sciences et de l'industrie / Cité des enfants (پاریس، فرانسه)", [1, 2, 3]),
    ("Mad Science (کانادا، با فعالیت جهانی)", [49, 11]),
    ("Museum of Ice Cream (آمریکا و سنگاپور)", [4]),
    ("مرکز ملک عبدالعزیز — Ithra (الربوه، عربستان)", [14, 19, 20, 21, 57]),
    ("موزه هنر اسلامی مالزی (IAMM) و مرکز گردشگری اسلامی (ITC)", [18, 38, 56]),
]
for name, ns in CASES:
    p = para(doc, "", before=6, after=2)
    run(p, name, size=11, color=NAVY, bold=True)
    p2 = para(doc, "", after=4, line=1.15)
    p2.paragraph_format.left_indent = Cm(0.4)
    run(p2, "مورد ", size=9.5, color=GRAY)
    for i, n in enumerate(ns):
        run(p2, "%s — %s" % (fa(n), titles[n]), size=9.5, color=BLUE, bold=True)
        run(p2, ("   |   " if i < len(ns) - 1 else ""), size=9.5, color=GRAY)

# ---------- بخش ۵: راهنمای اعتبارسنجی و گام‌های بعدی ----------
doc.add_page_break()
heading(doc, "بخش ۵ — راهنمای اعتبارسنجی، روش کار و گام‌های بعدی", 14)
hline(doc)
heading(doc, "راهنمای علامت‌ها", 12, color=BLUE, before=6, after=4)
p = para(doc, "", after=2)
run(p, "✅  ", size=10, color=GREEN, bold=True)
run(p, "نمونه تأییدشده: حقایق کلیدی (سال، اعداد، نام مکان) در تاریخ ۲۰۲۶/۱۱/۰۶ از ویکی‌پدیای انگلیسی "
       "(en.wikipedia.org) با جستجوی مستقیم صفحه‌های مربوطه تأیید شده‌اند.", size=10)
p = para(doc, "", after=6)
run(p, "⚠️  ", size=10, color=AMBER, bold=True)
run(p, "نمونهٔ دانش‌عمومی: مکان واقعی و شناخته‌شده است، اما مقالهٔ اختصاصی ویکی‌پدیایی ندارد یا جزئیات "
       "عددش در این مرحله بازرسی نشد؛ پیش از استفاده در اسناد رسمی، اعداد باید بازبینی شود.", size=10)
heading(doc, "روش تحقیق", 12, color=BLUE, before=6, after=4)
para(doc, "تحقیق در ۲۰۲۶/۱۱/۰۵–۰۶ با ۷ کارگر موازی تحقیقی (subagent) و اعتبارسنجی مستقیم از "
          "en.wikipedia.org (ابزار webfetch) انجام شد. دادهٔ پروفایل کیش نیز از همان منبع گردآوری شده است.", after=10)
heading(doc, "گام‌های پیشنهادی بعد", 12, color=BLUE, before=6, after=4)
steps = [
    "اولویت‌بندی: انتخاب ۱۵ تا ۲۰ مورد کلیدی (هسته) از ۶۱ مورد با معیار «تفرد کیش + تقاضای گردشگر + قابلیت درآمدزایی».",
    "برآورد بودجه و مساحت: تخمین سطح زیربنا، سرمایهٔ اولیه و هزینهٔ عملیاتی برای هر مورد هسته (با در نظر گرفتن مزیت منطقه آزاد).",
    "پلان‌مستر و زونینگ: چیدمان فضایی ۷ دسته روی سایت کیش (ساحل، بوم‌راه، دریاچهٔ هینگه، محوطهٔ Mica Mall).",
    "تحقیق عمیق: برای موارد کوتاه‌شده، تحلیل کامل مطالعات موردی (معماری، برنامه، مدل درآمدی) — شش سند موجود در پوشه از همین نوع هستند.",
    "بازنگری ذی‌نفعان: ارائهٔ فهرست نهایی به کارگزاران و سرمایه‌گذاران و تثبیت فازبندی اجرا.",
]
for i, s in enumerate(steps, 1):
    p = para(doc, "", after=3)
    run(p, "%s. " % fa(i), size=10, color=NAVY, bold=True)
    run(p, s, size=10)

doc.save(OUT)
print("saved:", OUT, "items:", total)
