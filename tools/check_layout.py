#!/usr/bin/env python3
"""Layout check for the STUDS.SG pages. Serves public/ locally and loads both pages at phone and desktop sizes,
with and without motion, then reports anything that looks broken:

  - the page scrolling sideways
  - text running into other text, or over a photo, button or field
  - text cut off at the edge of the screen
  - photos that fail to load, or that are cropped (people should always be whole)
  - the Donate button not visible on the first screen
  - script errors

Setup once:   pip install playwright && python3 -m playwright install chromium firefox webkit
Run:          python3 tools/check_layout.py          (Chrome only, quicker)
              python3 tools/check_layout.py --all    (Chrome, Firefox and Safari's engine)
Exit code 1 if anything was found.
"""
import asyncio, functools, http.server, pathlib, socketserver, sys, threading
from playwright.async_api import async_playwright

PUBLIC = pathlib.Path(__file__).resolve().parent.parent / "public"
PHONES = [(320, 568), (375, 667), (390, 844), (430, 932)]
DESKTOPS = [(1024, 768), (1280, 720), (1366, 768), (1440, 900), (1920, 1080), (2560, 1440), (3440, 1440)]

TEXT_CHECK = r"""() => {
  const texts = [], walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  while (walker.nextNode()) {
    const t = walker.currentNode; if (!t.textContent.trim()) continue;
    const el = t.parentElement;
    if (!el || el.closest('script,style,noscript,.sr-only,.sticky-donate,.skip,[hidden]')) continue;
    const cs = getComputedStyle(el); if (cs.visibility === 'hidden' || cs.display === 'none' || +cs.opacity === 0) continue;
    const r = document.createRange(); r.selectNodeContents(t);
    for (const q of r.getClientRects()) if (q.width >= 1 && q.height >= 1) texts.push({el, x: q.left, y: q.top, r: q.right, b: q.bottom});
  }
  const name = el => (typeof el.className === 'string' && el.className ? '.' + el.className.split(' ')[0] : el.tagName.toLowerCase()) + ' "' + (el.textContent || el.alt || '').trim().slice(0, 24) + '"';
  const found = new Set(), vw = document.documentElement.clientWidth;
  for (let i = 0; i < texts.length; i++) {
    const p = texts[i];
    if (p.r > vw + 1 || p.x < -1) found.add('text off the screen: ' + name(p.el));
    for (let j = i + 1; j < texts.length; j++) {
      const q = texts[j]; if (p.el === q.el || p.el.contains(q.el) || q.el.contains(p.el)) continue;
      const w = Math.min(p.r, q.r) - Math.max(p.x, q.x), h = Math.min(p.b, q.b) - Math.max(p.y, q.y);
      // tightly set headlines overlap their neighbours' line boxes a little; real collisions overlap by half a line or more
      if (w > 3 && h > 0.5 * Math.min(p.b - p.y, q.b - q.y)) found.add('text over text: ' + name(p.el) + ' / ' + name(q.el));
    }
  }
  const boxes = [...document.querySelectorAll('img, .btn, input, figure')].filter(b => {
    const cs = getComputedStyle(b); if (cs.display === 'none' || cs.visibility === 'hidden') return false;
    if (b.closest('.sticky-donate') || cs.position === 'fixed') return false;   // the phone Donate bar floats over the page on purpose
    const ph = b.closest('.hero-photo'); return !(ph && getComputedStyle(ph).clipPath !== 'none');
  });
  for (const b of boxes) {
    const br = b.getBoundingClientRect(); if (br.width < 2 || br.height < 2) continue;
    for (const p of texts) {
      if (b.contains(p.el) || p.el.contains(b)) continue;
      const w = Math.min(p.r, br.right) - Math.max(p.x, br.left), h = Math.min(p.b, br.bottom) - Math.max(p.y, br.top);
      if (w > 1 && h > 0.3 * (p.b - p.y)) found.add('text over ' + b.tagName.toLowerCase() + ': ' + name(p.el));
    }
  }
  return [...found];
}"""
PHOTO_CHECK = r"""() => {
  const out = [];
  for (const img of document.images) {
    if (img.complete && img.naturalWidth === 0) { out.push('photo missing: ' + img.src.split('/').pop()); continue; }
    if (!img.closest('.wall-item, .social-item, .race-feature, .cause-photo') || !img.naturalWidth) continue;
    const box = img.getBoundingClientRect(), frame = img.parentElement.getBoundingClientRect();
    if (frame.width < 2) continue;
    const s = Math.max(box.width / img.naturalWidth, box.height / img.naturalHeight);
    const vx = Math.min(frame.width, img.naturalWidth * s) / (img.naturalWidth * s), vy = Math.min(frame.height, img.naturalHeight * s) / (img.naturalHeight * s);
    if (vx < 0.9 || vy < 0.9) out.push(`photo cropped: ${img.src.split('/').pop()} shows ${Math.round(vx * 100)}% of its width and ${Math.round(vy * 100)}% of its height`);
  }
  return out;
}"""
FIRST_SCREEN = """() => { const a = document.querySelectorAll('.hero-actions .btn'); if (!a.length) return true;
  return a[a.length - 1].getBoundingClientRect().bottom <= innerHeight; }"""

class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *args): pass

def serve():
    handler = functools.partial(Quiet, directory=str(PUBLIC))
    httpd = socketserver.TCPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{httpd.server_address[1]}/"

async def check(browser, base, page_name, w, h, phone, motion):
    opts = dict(viewport={"width": w, "height": h}, reduced_motion="no-preference" if motion else "reduce")
    if phone and browser.browser_type.name != "firefox": opts.update(is_mobile=True, has_touch=True)
    ctx = await browser.new_context(**opts); pg = await ctx.new_page(); errors = []
    pg.on("pageerror", lambda e: errors.append("script error: " + str(e)[:120]))
    await pg.goto(base + page_name, wait_until="networkidle"); await pg.evaluate("document.fonts.ready"); await pg.wait_for_timeout(250)
    issues = [] if await pg.evaluate(FIRST_SCREEN) else ["Donate button below the first screen"]
    height = await pg.evaluate("document.documentElement.scrollHeight"); sideways = 0
    for y in range(0, height + h, max(300, h // 2)):
        await pg.evaluate(f"scrollTo(0, {y})"); await pg.wait_for_timeout(60 if motion else 30)
        sideways = max(sideways, await pg.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth"))
        if not motion: issues += await pg.evaluate(TEXT_CHECK)   # with motion, things move on purpose
    await pg.wait_for_timeout(500)
    issues += await pg.evaluate(PHOTO_CHECK)
    if sideways > 0: issues.append(f"page scrolls sideways by {sideways}px")
    await ctx.close()
    return sorted(set(issues + errors))

async def main():
    base = serve()
    names = ["chromium", "firefox", "webkit"] if "--all" in sys.argv else ["chromium"]
    problems = 0
    async with async_playwright() as p:
        for name in names:
            browser = await getattr(p, name).launch()
            for page_name in ("index.html", "about.html"):
                for (w, h) in PHONES + DESKTOPS:
                    for motion in ((False, True) if page_name == "index.html" else (False,)):
                        issues = await check(browser, base, page_name, w, h, (w, h) in PHONES, motion)
                        label = f"{name:8} {page_name:10} {w}x{h} {'motion' if motion else 'still '}"
                        print(label, "OK" if not issues else "\n    " + "\n    ".join(issues), flush=True)
                        problems += bool(issues)
            await browser.close()
    print("\nAll clear." if not problems else f"\n{problems} runs found something to look at.")
    sys.exit(1 if problems else 0)

asyncio.run(main())
