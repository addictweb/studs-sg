#!/usr/bin/env python3
"""Prepare a photo for one of the photo walls and print the markup to paste into public/index.html.

  python3 tools/photo.py <original photo> <new name> <shape> [focus]

  new name   e.g. training-swim or race-busselton (no extension; use a name that hasn't been used before)
  shape      portrait (3:4), upright (2:3), landscape (4:3) or wide (3:2): pick the one closest to the photo,
             so that nobody gets cut off
  focus      optional, where to keep when trimming to the shape, as "x y" fractions; default "0.5 0.5" (centre)

Writes four files to public/images/: <name>.jpg, <name>-600.jpg, <name>.webp and <name>-600.webp, with no
EXIF data (EXIF can hold the place a photo was taken). Needs Pillow: pip install Pillow
"""
import pathlib, sys
from PIL import Image, ImageOps

SHAPES = {"portrait": (750, 1000), "upright": (667, 1000), "landscape": (1000, 750), "wide": (1000, 667)}
SIZES = "(min-width: 1440px) 384px, (min-width: 960px) 27vw, calc(50vw - 25px)"
if len(sys.argv) < 4 or sys.argv[3] not in SHAPES:
    sys.exit(__doc__)
src, name, shape = pathlib.Path(sys.argv[1]), sys.argv[2], sys.argv[3]
fx, fy = (float(v) for v in (sys.argv[4].split() if len(sys.argv) > 4 else ("0.5", "0.5")))
out = pathlib.Path(__file__).resolve().parent.parent / "public" / "images"
w, h = SHAPES[shape]
im = ImageOps.fit(ImageOps.exif_transpose(Image.open(src)).convert("RGB"), (w, h), Image.LANCZOS, centering=(fx, fy))
small = im.resize((600, round(h * 600 / w)), Image.LANCZOS)
for img, suffix in ((im, ""), (small, "-600")):
    img.save(out / f"{name}{suffix}.jpg", "JPEG", quality=78, optimize=True, progressive=True)
    img.save(out / f"{name}{suffix}.webp", "WEBP", quality=74, method=6)
print(f"""Wrote {name}.jpg, {name}-600.jpg, {name}.webp and {name}-600.webp to {out}

Paste this into the shortest column of the right wall in public/index.html, and change the alt text
to say who is in the photo and what is happening (no names):

<figure class="wall-item plx {shape}"><picture><source type="image/webp" srcset="images/{name}-600.webp 600w, images/{name}.webp {w}w" sizes="{SIZES}"><img src="images/{name}.jpg" srcset="images/{name}-600.jpg 600w, images/{name}.jpg {w}w" sizes="{SIZES}" width="{w}" height="{h}" loading="lazy" decoding="async" alt="DESCRIBE THE PHOTO"></picture></figure>
""")
