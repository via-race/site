#!/usr/bin/env python3
"""
One-off migration: pull content from the old Strapi CMS (cms.via-race.com)
into this Hugo site as Markdown + YAML, and download all images locally so
the Strapi server and its CDN can be switched off.

Usage:
    python3 tools/migrate_from_strapi.py            # English
    python3 tools/migrate_from_strapi.py --locale de # German into content/de (see README)

Only needs the Python standard library.
"""
import argparse
import json
import os
import re
import sys
import urllib.parse
import urllib.request

API = "https://cms.via-race.com/api"
UA = {"User-Agent": "Mozilla/5.0 (via-race migration)"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get(path, **params):
    q = urllib.parse.urlencode(params, safe="[]*,")
    url = f"{API}/{path}?{q}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
        return json.load(r)


def download(url, dest):
    if os.path.exists(dest):
        return
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120) as r, open(dest, "wb") as f:
        f.write(r.read())


def best_url(media):
    """Original upload (run tools/optimize_images.py afterwards to shrink to 1920px)."""
    return media["url"], media.get("ext", ".jpg").lower()


def yq(s):
    """Quote a scalar for YAML front matter."""
    if s is None:
        return '""'
    return json.dumps(str(s).strip(), ensure_ascii=False)


def clean_md(md, title=""):
    md = md.replace("\r\n", "\n").lstrip()
    # drop a leading heading that just repeats the title (the layout shows the title)
    first, _, rest = md.partition("\n")
    norm = lambda x: re.sub(r"[^a-z0-9]", "", x.lower())
    if first.startswith("#") and norm(first) == norm(title):
        md = rest
    # Strapi sometimes stores empty heading markers
    md = re.sub(r"^#{1,6}\s*$", "", md, flags=re.M)
    return md.strip() + "\n"


def migrate_posts(locale, content_dir):
    data = get("blog-posts", **{"populate": "*", "pagination[pageSize]": 200, "locale": locale})["data"]
    for p in data:
        slug = p["slug"]
        bundle = os.path.join(content_dir, "blog", slug)
        os.makedirs(bundle, exist_ok=True)
        fm = ["---", f"title: {yq(p['Title'])}", f"description: {yq(p.get('Description'))}",
              f"date: {p['publishedAt']}"]
        if p.get("updatedAt"):
            fm.append(f"lastmod: {p['updatedAt']}")
        cat = p.get("blog_post_category")
        if cat:
            fm.append(f"categories: [{yq(cat['slug'])}]")
        tags = p.get("blog_post_tags") or []
        if tags:
            fm.append("tags: [" + ", ".join(yq(t["slug"]) for t in tags) + "]")
        hi = p.get("HeaderImage")
        if hi:
            u, ext = best_url(hi)
            download(u, os.path.join(bundle, "cover" + ext))
            fm.append(f"image: cover{ext}")
        gallery = []
        for i, g in enumerate(p.get("Gallery") or [], 1):
            u, ext = best_url(g)
            name = f"gallery-{i:02d}{ext}"
            download(u, os.path.join(bundle, name))
            gallery.append(name)
        if gallery:
            fm.append("gallery:")
            fm += [f"  - {g}" for g in gallery]
        seo = p.get("SEO") or {}
        if seo.get("MetaDescription"):
            fm.append(f"seo_description: {yq(seo['MetaDescription'])}")
        fm.append("---")
        with open(os.path.join(bundle, "index.md"), "w") as f:
            f.write("\n".join(fm) + "\n\n" + clean_md(p["Content"], p["Title"]))
        print("post", slug, len(gallery), "images")


def migrate_faq(locale, content_dir):
    d = get("faq", populate="*", locale=locale)["data"]
    sections = [("ApplicationQuestions", "Application questions"), ("FinancialQuestions", "Financial questions"),
                ("TheRoute", "The route"), ("Equipment", "Equipment"), ("Miscellaneous", "Miscellaneous")]
    out = {"last_updated": d.get("GlobalInfos"), "sections": [], "timeline": []}
    for key, title in sections:
        items = [{"q": x["Question"].strip(), "a": (x.get("Answer") or "").strip()} for x in d.get(key) or []]
        out["sections"].append({"id": re.sub(r"[^a-z]+", "-", title.lower()).strip("-"), "title": title, "items": items})
    for t in d.get("Timeline") or []:
        out["timeline"].append({"date": t["Date"], "info": (t.get("Infos") or "").strip()})
    seo = d.get("SEO") or {}
    page = {"title": "FAQ", "description": seo.get("MetaDescription") or "", "layout": "faq", **out}
    os.makedirs(content_dir, exist_ok=True)
    # JSON front matter keeps multi-line Markdown answers safe and is editable in Pages CMS
    with open(os.path.join(content_dir, "faq.md"), "w") as f:
        f.write(json.dumps(page, ensure_ascii=False, indent=2) + "\n")
    print("faq", sum(len(s["items"]) for s in out["sections"]), "questions")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--locale", default="en")
    a = ap.parse_args()
    content_dir = os.path.join(ROOT, "content", a.locale)
    migrate_posts(a.locale, content_dir)
    migrate_faq(a.locale, content_dir)


if __name__ == "__main__":
    sys.exit(main())
