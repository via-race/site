#!/usr/bin/env python3
"""Shrink images in content bundles to max 1920px JPEG (q82) and fix references in index.md.
Run after adding photos:  python3 tools/optimize_images.py   (needs: pip install pillow)"""
import glob, os
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for md in glob.glob(os.path.join(ROOT, "content", "*", "**", "index.md"), recursive=True):
    d = os.path.dirname(md)
    s = open(md).read()
    for f in sorted(glob.glob(d + "/*")):
        base = os.path.basename(f)
        stem, ext = os.path.splitext(base)
        if ext.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            continue
        im = Image.open(f)
        if ext.lower() in (".jpg", ".jpeg") and max(im.size) <= 1920 and os.path.getsize(f) < 600_000:
            continue
        im = ImageOps.exif_transpose(im).convert("RGB")
        im.thumbnail((1920, 1920))
        new = stem + ".jpg"
        im.save(os.path.join(d, new), quality=82, optimize=True, progressive=True)
        if base != new:
            os.remove(f)
            s = s.replace(base, new)
    open(md, "w").write(s)
print("done")
