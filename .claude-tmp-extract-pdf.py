# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
from pypdf import PdfReader

path = "D:\\\u6d4f\u89c8\u5668\\AI \u4e16\u754c\u89c2\u5bdf\u4e0e\u5e72\u9884\u6a21\u62df\u5668\u4ea7\u54c1\u4e0e\u6280\u672f\u5b9e\u65bd\u8ba1\u5212\u4e66.pdf"
r = PdfReader(path)
print("encrypted:", r.is_encrypted)
print("pages:", len(r.pages))
out = []
for i, p in enumerate(r.pages):
    out.append(f"===== PAGE {i+1} =====")
    out.append(p.extract_text() or "")
with open("D:\\python-code\\ai-world-simulator\\.claude-tmp-plan.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("written")
