#!/usr/bin/env python3
"""Recompute the Content-Security-Policy hashes for the inline scripts in public/index.html and write them
into public/_headers. Run it after any change to either script: python3 tools/update_csp.py"""
import base64, hashlib, pathlib, re

root = pathlib.Path(__file__).resolve().parent.parent
site = root / "public" if (root / "public" / "index.html").exists() else root
html = (site / "index.html").read_text(encoding="utf-8")
hashes = []
for attrs, body in re.findall(r"<script([^>]*)>(.*?)</script>", html, flags=re.S):
    if "type=" in attrs and "javascript" not in attrs:
        continue  # JSON data blocks are never run, so they need no hash
    digest = hashlib.sha256(body.encode("utf-8")).digest()
    hashes.append("'sha256-" + base64.b64encode(digest).decode() + "'")
headers = site / "_headers"
text = headers.read_text(encoding="utf-8")
text = re.sub(r"(Content-Security-Policy:[^\n]*?)script-src [^;]*;",
              lambda m: m.group(1) + "script-src 'self' " + " ".join(hashes) + ";", text, count=1)
headers.write_text(text, encoding="utf-8")
print(f"Updated {len(hashes)} script hashes in {headers}")
