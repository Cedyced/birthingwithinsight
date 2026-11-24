#!/usr/bin/env python3
"""Automated checks for the built site in docs/ (stdlib only).

Usage: python3 tools/check_site.py        → exit code 1 if any ERROR
Checks: internal links & assets resolve, every page has title/description/canonical/
hreflang pair, <img> alt present, lang attribute, legacy Wix URLs exist, palette contrast.
"""
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse

DOCS = Path(__file__).resolve().parent.parent / 'docs'
# Path prefix from build.py (non-empty while testing on <user>.github.io/<repo>/)
BASE = (re.search(r"^BASE = '([^']*)'", (DOCS.parent / 'build.py').read_text(), re.M) or [None, ''])[1]
LEGACY = ['/about/', '/contact/', '/faq/', '/book-online/', '/blog/',
          '/fr/', '/fr/about/', '/fr/contact/', '/fr/faq/', '/fr/blog/', '/fr/book-online/',
          '/service-page/in-person-prenatal-class/', '/service-page/full-day-prenatal-newborn-care/',
          '/service-page/cours-prénatal-en-présentiel-1/',
          '/post/navigating-the-postpartum-period-with-confidence/', '/post/relieving-pregnancy-discomfort-naturally/',
          '/post/preparing-for-a-positive-birth-experience/', '/post/the-role-of-massage-in-labor/',
          '/post/exploring-different-birthing-positions/', '/post/supporting-your-partner-during-labor/',
          '/post/understanding-the-stages-of-labor/', '/post/empowering-women-through-knowledge-and-support/']

errors, warnings = [], []


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.imgs, self.meta, self.hreflang, self.title = [], [], {}, {}, ''
        self.lang, self.canonical, self._in_title, self.h1 = None, None, False, 0
        self.refresh = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang')
        elif tag == 'a' and a.get('href'):
            self.links.append(a['href'])
        elif tag == 'link':
            if a.get('rel') == 'canonical':
                self.canonical = a.get('href')
            elif a.get('rel') == 'alternate' and a.get('hreflang'):
                self.hreflang[a['hreflang']] = a.get('href')
            elif a.get('rel') == 'stylesheet' or a.get('rel') == 'icon':
                self.links.append(a.get('href'))
        elif tag == 'img':
            self.imgs.append(a)
        elif tag == 'script' and a.get('src'):
            self.links.append(a['src'])
        elif tag == 'meta':
            if a.get('name'):
                self.meta[a['name']] = a.get('content', '')
            if a.get('http-equiv') == 'refresh':
                self.refresh = True
                self.links.append(a.get('content', '').split('url=', 1)[-1])
        elif tag == 'title':
            self._in_title = True
        elif tag == 'h1':
            self.h1 += 1

    def handle_endtag(self, tag):
        if tag == 'title':
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data


def resolve(href):
    path = unquote(urlparse(href).path)
    if BASE and path.startswith(BASE + '/'):
        path = path[len(BASE):]
    target = DOCS / path.lstrip('/')
    if path.endswith('/') or target.is_dir():
        target = target / 'index.html'
    return target


def lum(hex_):
    rgb = [int(hex_[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    rgb = [c / 12.92 if c <= .03928 else ((c + .055) / 1.055) ** 2.4 for c in rgb]
    return .2126 * rgb[0] + .7152 * rgb[1] + .0722 * rgb[2]


def contrast(a, b):
    la, lb = sorted([lum(a), lum(b)], reverse=True)
    return (la + .05) / (lb + .05)


def main():
    if not DOCS.exists():
        sys.exit('docs/ not found — run python3 build.py first')
    pages = sorted(DOCS.rglob('*.html'))
    titles = {}
    for f in pages:
        rel = '/' + str(f.relative_to(DOCS)).replace('index.html', '')
        p = Page()
        p.feed(f.read_text())
        for href in p.links:
            if not href or href.startswith(('http', 'mailto:', 'tel:', '#', '//')):
                continue
            if not resolve(href).exists():
                errors.append(f'{rel}: broken link → {href}')
        for img in p.imgs:
            if 'alt' not in img:
                errors.append(f'{rel}: <img src={img.get("src")}> missing alt')
            src = img.get('src', '')
            if src.startswith('/') and not resolve(src).exists():
                errors.append(f'{rel}: missing image {src}')
        if p.refresh:
            continue  # redirect stub
        if not p.lang:
            errors.append(f'{rel}: <html> has no lang')
        if not p.title.strip():
            errors.append(f'{rel}: empty <title>')
        titles.setdefault(p.title.strip(), []).append(rel)
        if 'noindex' in p.meta.get('robots', ''):
            continue
        if not p.meta.get('description'):
            errors.append(f'{rel}: no meta description')
        if not p.canonical:
            errors.append(f'{rel}: no canonical')
        if not {'en-CA', 'fr-CA'} <= set(p.hreflang):
            errors.append(f'{rel}: missing hreflang pair')
        else:
            for lang, url in p.hreflang.items():
                if not resolve(url).exists():
                    errors.append(f'{rel}: hreflang {lang} → {url} does not exist')
        if p.h1 != 1:
            warnings.append(f'{rel}: {p.h1} <h1> elements (expected 1)')
        if len(p.meta.get('description', '')) > 170:
            warnings.append(f'{rel}: meta description {len(p.meta["description"])} chars (>170)')
    for t, where in titles.items():
        if len(where) > 1:
            warnings.append(f'duplicate <title> "{t}" on {where}')
    for url in LEGACY:
        if not resolve(url).exists():
            errors.append(f'legacy Wix URL not served: {url}')
    for fname in ('sitemap.xml', 'robots.txt', '.nojekyll', '404.html'):
        if not (DOCS / fname).exists():
            errors.append(f'missing docs/{fname}')

    # Text/background pairs used in site.css — must meet WCAG AA (4.5:1 normal text)
    pairs = [('#3A3D39', '#F4F1EA', 'body text on linen'), ('#595C55', '#F4F1EA', 'soft text on linen'),
             ('#3F4A3D', '#F4F1EA', 'headings on linen'), ('#FBFAF6', '#4A5A48', 'button text on moss'),
             ('#4A5A48', '#F4F1EA', 'links on linen'), ('#5B6A58', '#F4F1EA', 'eyebrow (sage ink) on linen'),
             ('#595C55', '#E9E6DC', 'soft text on stone'), ('#595C55', '#E2E7DC', 'soft text on sage'),
             ('#4F5C4D', '#E2E7DC', 'tag on sage'), ('#7A5344', '#EEE8DC', 'FR tag on sand'),
             ('#4A5A48', '#E9E6DC', 'tag on stone'), ('#CDD4C4', '#3B4939', 'footer text on deep moss'),
             ('#C3CBB9', '#3B4939', 'footer legal on deep moss'), ('#C9D3BD', '#3B4939', 'footer headings'),
             ('#5B6A58', '#FBFAF6', 'card meta (sage ink) on card'), ('#5B6A58', '#E9E6DC', 'sage ink on stone')]
    for fg, bg, label in pairs:
        r = contrast(fg, bg)
        if r < 3:
            errors.append(f'contrast {r:.2f}:1 — {label} ({fg} on {bg})')
        elif r < 4.5:
            warnings.append(f'contrast {r:.2f}:1 (AA large-text only) — {label} ({fg} on {bg})')

    print(f'Checked {len(pages)} HTML files.')
    for w in warnings:
        print('WARN ', w)
    for e in errors:
        print('ERROR', e)
    print(f'{len(errors)} error(s), {len(warnings)} warning(s)')
    sys.exit(1 if errors else 0)


if __name__ == '__main__':
    main()
