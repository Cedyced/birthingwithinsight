# Birthing With Insight — website

Static, bilingual (EN/FR) site for https://www.birthingwithinsight.ca, hosted on GitHub Pages.
Requirements and design rules live in [CLAUDE.md](CLAUDE.md).

## Everyday use
```bash
python3 build.py                          # build the site into docs/
python3 tools/check_site.py               # check links, images, SEO tags, contrast
python3 -m http.server 8000 -d docs       # preview at http://localhost:8000
```

### Add a blog post
Create `content/blog/en/<slug>.md` (or `fr/`), put its image in `src/assets/img/blog/`, then build:
```markdown
---
title: My new post
date: 2026-10-01
image: blog/my-new-post.jpg
excerpt: One or two sentences shown on the blog cards.
---

First paragraph…
```

### Turn on online booking (cal.com)
1. Create event types in cal.com for each class.
2. In `build.py` set `CAL['username']` and each service's `cal_event` slug.
3. Rebuild. Until then, class pages show "call or email to book".

### Contact form (optional)
Create a free form at formspree.io, put its id in `FORMSPREE_ID` in `build.py`, rebuild.

## Publishing on GitHub Pages
1. Create a GitHub repository and push this folder.
2. Repository → Settings → Pages → *Deploy from a branch* → `main` / `/docs`.
3. To test before switching the domain, set `BASE = '/<repo-name>'` in `build.py`, rebuild, and visit `https://<user>.github.io/<repo-name>/`. Set it back to `''` before going live.
4. Going live: in Settings → Pages set the custom domain `www.birthingwithinsight.ca`, then at your DNS provider
   add a `CNAME` record `www` → `<user>.github.io` and `A` records for the apex domain to
   185.199.108.153, 185.199.109.153, 185.199.110.153, 185.199.111.153. Enable "Enforce HTTPS" once available.
5. Cancel the Wix plan only after the new site is live and verified.
