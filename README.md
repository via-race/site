# VIA Race website (static)

Static rebuild of [via-race.com](https://via-race.com) with **Hugo**, hosted for free on **GitHub Pages**, styled with the VIA brand book (CW0426 Brand Development).

```
content/en/            all text, as Markdown (one folder per Diary post, photos next to it)
data/race.yaml         current chapter: dates, start/finish, distance (drives the stats bar)
data/sponsors.yaml     "Supported by" logos
i18n/en.yaml           UI strings (buttons, labels) for translation
layouts/               HTML templates (no theme dependency)
assets/css/main.css    the whole design, brand colours as CSS variables
assets/js/main.js      ~2 KB: mobile menu, lightbox, newsletter, tracker click-to-load
assets/svg/            VIA icon + wordmark, vector-extracted from the brand PDF
tools/                 one-off Strapi migration + image optimiser
```

## Run locally

```bash
brew install hugo            # or: pip install hugo   (needs Hugo extended >= 0.158)
hugo server                  # http://localhost:1313, live reload
```

## Publish

1. Create a GitHub repo (e.g. `via-race`) and push this folder to `main`.
2. Repo **Settings > Pages > Source: GitHub Actions**. The workflow in `.github/workflows/deploy.yml` builds and deploys on every push (about 1 minute).
3. Custom domain: **Settings > Pages > Custom domain = `via-race.com`**, tick *Enforce HTTPS*. At the DNS provider (Cloudflare) point the apex to GitHub Pages:
   `A 185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153` and `CNAME www -> <owner>.github.io`. If Cloudflare proxies the record, set SSL mode to *Full*.
4. Keep the old server running until the new URL is checked, then switch DNS.

## How to add things

**A Diary post:** create `content/en/blog/<url-slug>/index.md`, drop `cover.jpg` and photos in the same folder:

```markdown
---
title: "Gates of the North"
description: "One line for cards and Google."
date: 2026-10-10
categories: ["stories"]          # interviews | stories | places | news | podcast | gallery
tags: ["chapter-3", "riders"]
image: cover.jpg
gallery: [photo-1.jpg, photo-2.jpg]
---
Text in Markdown. Single line breaks are kept, like on the old site.
```

Run `python3 tools/optimize_images.py` before committing big phone photos (shrinks to 1920px JPEG). The **Gallery** page fills itself from post galleries, grouped by chapter tag.

**A new page:** `content/en/<name>.md` with `title` + `description`, then add it to `[menus]` in `hugo.toml` if it needs a nav link.

**FAQ:** `content/en/faq.md` (sections, questions, timeline). **Race dates / stats bar:** `data/race.yaml`. **Next chapter:** update `data/race.yaml`, the home page front matter and add a `chapter-4` tag folder.

**Shortcodes** usable in any Markdown: `{{< pillars >}}` (cards: `- emoji | title | text`), `{{< button href="..." >}}Label{{< /button >}}`, Hugo's built-in `{{< youtube ID >}}`.

### Editing without Git (optional)

Use the GitHub web editor: open the repo and press `.`, or edit a file and commit from the browser. Every commit to `main` redeploys the site. For a form-based editor with photo upload, connect the repo to [Pages CMS](https://pagescms.org) (log in with GitHub, no server needed).

## Languages

The old site had 7 languages in Strapi. English is migrated; the structure is ready for more:

```bash
python3 tools/migrate_from_strapi.py --locale de   # pulls DE posts + FAQ into content/de/
```

then copy `i18n/en.yaml` to `i18n/de.yaml`, translate the strings, uncomment the language block in `hugo.toml`, and add `content/de/_index.md`, `about.md`, etc. URLs become `/de/...` like before.

**Run the migration before the Strapi server is switched off.** All images are already copied into this repo, so nothing depends on `cms.via-race.com` or `cdn.via-race.com` any more.

## Why these tools (frontend proposal)

| Layer | Choice | Why | Considered |
|---|---|---|---|
| Generator | **Hugo** | Single binary, no `node_modules`/Ruby to maintain, builds in seconds, first-class multilingual (7 languages existed), built-in image resizing to WebP, taxonomies for Diary categories/tags | **Jekyll**: native to Pages but multilingual needs a plugin, which forces a custom Actions build anyway; slower; Ruby toolchain. **Astro**: great if the site grows interactive features (live map, results tables), but adds a Node toolchain Ian would have to keep updated. **Eleventy**: flexible, but more DIY for i18n and images. |
| CSS | **Plain modern CSS** with brand tokens (`--via-coral`, `--via-slate`...) | One 20 KB file, no build step, easy for anyone to tweak | Tailwind (the old site used it): needs Node + PostCSS, utility soup in templates is harder for non-developers |
| JS | **Vanilla, ~2 KB** | Only a menu, a lightbox (native `<dialog>`), a newsletter POST and click-to-load tracker | Alpine.js would be the next step if more interactivity appears; no SPA framework needed |
| Fonts | **Jost** (self-hosted) | Open-source geometric sans close to the brand font *Dunbar Text*, which is commercial. Self-hosting avoids Google Fonts (GDPR) | If a Dunbar Text web licence is bought, swap the `@font-face` in `layouts/_partials/head.html` |
| Hosting | **GitHub Pages + Actions** | Free, HTTPS, CDN, deploy on push | Cloudflare Pages / Netlify are equally free and also work with this repo unchanged |
| Editing | **Markdown in Git**, optional **Pages CMS** | Content is portable plain text; no database or server | Keeping Strapi means paying for and patching a server |

## What changed vs the old stack

Old: Nuxt (SSR) + self-hosted Strapi CMS (`cms.via-race.com`) + CDN for uploads + Cloudflare Worker (newsletter) + Shopify storefront API.
New: static files on GitHub Pages. Running cost for the website itself: **0** (only the domain).

Kept as-is (external, free/paid separately): MADCAP live tracker (click-to-load embed + link), newsletter Cloudflare Worker -> Mailchimp (same endpoint, `params.newsletterEndpoint`), YouTube hero video (`params.heroYouTube`, loads after the page and only on desktop).

Not carried over: user login routes, empty `/apply` and `/shop` pages (the Shopify store can be linked from the menu if it is still used), translations (see Languages). Old URLs for posts, categories and tags are identical, so links and Google results keep working.

Text tweaks to review with Ian: the Privacy page now also lists GitHub Pages as host and mentions the YouTube/tracker embeds; the About page uses the same wording, just formatted.
