#!/usr/bin/env python3
"""Make the link-preview image: the picture WhatsApp and social apps show when the site's address is shared.

  python3 tools/share_image.py <photo> <new name> "<caption line 1>" ["<caption line 2>"]

  photo      a 16:9 photo already in public/images, e.g. hero-phuket-1400.jpg
  new name   e.g. studs-share-2027 (no extension; use a name that hasn't been used before, because apps keep previews)
  caption    one or two short lines for the bottom left; avoid wording that will go out of date

Writes public/images/<new name>.jpg (1200 x 630). Afterwards, change og:image and twitter:image in both pages and
the two "image" entries in the structured data of index.html to the new name, and delete the old file.
Needs Playwright and Pillow: pip install playwright Pillow; python3 -m playwright install chromium
"""
import asyncio, functools, html, http.server, io, pathlib, socketserver, sys, threading
from PIL import Image
from playwright.async_api import async_playwright

if len(sys.argv) < 4:
    sys.exit(__doc__)
public = pathlib.Path(__file__).resolve().parent.parent / "public"
photo, name, caption = sys.argv[1], sys.argv[2], "<br>".join(html.escape(line) for line in sys.argv[3:5])
if not (public / "images" / photo).is_file():
    sys.exit(f"No such photo: public/images/{photo}")
PAGE = f"""<!doctype html><meta charset="utf-8"><style>
@font-face {{ font-family: "Archivo"; src: url("/fonts/archivo-latin-wght-normal.woff2") format("woff2"); font-weight: 100 900; }}
* {{ margin: 0; box-sizing: border-box; }}
body {{ width: 1200px; height: 630px; background: #0C1A33; color: #F3F5F6; font-family: "Archivo", sans-serif; position: relative; overflow: hidden; }}
.t {{ position: absolute; left: 64px; white-space: nowrap; }}
.word {{ top: 52px; font-weight: 900; font-size: 43px; letter-spacing: -.01em; line-height: 1; }}
.word b {{ color: #7DC242; font-weight: 900; }}
.head {{ top: 222px; font-weight: 900; font-size: 85px; letter-spacing: -.01em; line-height: .9; text-transform: uppercase; }}
.sub {{ top: 387px; font-weight: 700; font-size: 34px; line-height: 1.15; }}
.cap {{ top: 517px; font-size: 22px; line-height: 29px; color: #A9B4C6; }}
img {{ position: absolute; left: 600px; top: 146px; width: 600px; height: 338px; object-fit: cover; }}
</style>
<div class="t word">STUDS<b>.</b>SG</div>
<div class="t head">Ordinary<br>men.</div>
<div class="t sub">Extraordinary challenges.</div>
<div class="t cap">{caption}</div>
<img src="/images/{html.escape(photo)}" alt="">"""


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


async def main():
    server = socketserver.TCPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(public)))
    threading.Thread(target=server.serve_forever, daemon=True).start()
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1200, "height": 630}, device_scale_factor=1)
        await page.goto(f"http://127.0.0.1:{server.server_address[1]}/robots.txt")   # gives the page an address, so /fonts and /images load
        await page.set_content(PAGE, wait_until="networkidle")
        await page.evaluate("document.fonts.ready")
        shot = await page.screenshot()
        await browser.close()
    out = public / "images" / f"{name}.jpg"
    Image.open(io.BytesIO(shot)).convert("RGB").save(out, "JPEG", quality=86, optimize=True, progressive=True)
    print(f"Wrote {out}")


asyncio.run(main())
