# -*- coding: utf-8 -*-
import os
os.chdir(os.path.dirname(os.path.abspath(__file__)))
for f in sorted(os.listdir("تصاویر")):
    print("%s  %d" % (f, os.path.getsize(os.path.join("تصاویر", f))))
