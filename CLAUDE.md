# Birthing With Insight — static site

Static rebuild of the Wix site https://www.birthingwithinsight.ca, hosted on **GitHub Pages**.
This file is the single source of truth for requirements. Read it before any change.

## The business
- **Name: "Birthing With Insight"** (formerly "Birthing With Insight & Integrity" — don't use the old name anywhere).
- Prenatal education in Orléans (Ottawa), ON. Founder: **Ashley**, Registered Nurse in labour & delivery since 2010, mother of two, Montfort Hospital for 10+ years.
- Classes are small, hands-on, and include the **support person**. Techniques come from yoga teachers, massage therapists, midwives and obstetricians.
- Location: Ottawa Medical Group building, **4289 Innes Road, 2nd floor (OMG obstetricians' offices), Orléans, ON K1E 0A8**.
- Contact: **1-343-348-9883** · **registration@birthingwithinsight.ca**
- Services (prices in CAD, fee covers mother-to-be **plus one support person**):
  | Service | Lang | Price | Notes |
  |---|---|---|---|
  | In Person Prenatal Class | EN | $70 | 2.5 h session |
  | Cours prénatal en présentiel | FR | $70 | 2.5 h session |
  | Full Day Prenatal & Newborn Care | EN | $150 | 9:30 a.m.–4:30 p.m. Morning: maternal recovery + newborn care/feeding (Certified Lactation Consultant); 45-min lunch; afternoon: labour & delivery. Covered by most insurance |
- Ideal timing: 25–35 weeks gestation (everyone welcome at any point).

## Requirements
1. **Bilingual** (class descriptions and Ashley's quote on About were supplied in English only and translated by Claude — FR needs review): English at `/`, French at `/fr/`. Every page has a language switcher to its counterpart. French copy comes from the live `/fr` pages; where the live site had none (service descriptions, Full Day page), Claude translated it — **flag these for Ashley to review** (marked `<!-- FR: review -->` in source).
2. **Pages** (both languages): Home, About, Classes (was "Book Online" — list + booking), FAQ, Contact, Blog index, blog posts.
   Old Wix URLs must keep working: `/about`, `/contact`, `/faq`, `/book-online`, `/blog`, `/post/<slug>`, `/service-page/<slug>` — use folder `index.html` paths or redirect stubs.
3. **Booking**: Wix Bookings is replaced by a **cal.com** embed. Config lives in `build.py` (`CAL`). Account: `ashley-burgins-ya1eov` — events `in-person-prenatal-class`, `cours-prenatal-en-presentiel`, `full-day-prenatal`. Card "Book now" buttons open a cal.com popup (plain link fallback); class pages embed the calendar inline.
4. **Contact**: no server. Show phone/email/address/map. Optional form via Formspree when `FORMSPREE_ID` in `build.py` is set.
5. **Blog**: Markdown files in `content/blog/<lang>/<slug>.md` with front matter (`title`, `date`, `image`, `excerpt`). Only one French post exists; the FR blog index also lists English posts, labelled "(en anglais)".
6. **SEO**: per-page `<title>`, meta description, canonical, `hreflang` pairs, Open Graph image, `sitemap.xml`, `robots.txt`, LocalBusiness JSON-LD on the home page. Custom domain via `docs/CNAME`.
7. **No framework, no Node.** Python 3 stdlib only (`python3 build.py`). Output goes to `docs/` (GitHub Pages serves `main` → `/docs`). Never hand-edit `docs/`.

## Design direction (prenatal audience)
- Feeling: **calm, warm, reassuring, trustworthy**. Expectant parents may be anxious; the site should feel like a gentle exhale. No harsh contrasts, no urgency tricks, no pushy popups.
- Zen, holistic, grounded: natural linen/stone/sage/moss tones, soft organic shapes (rounded corners, gentle curves, blob accents), generous whitespace, botanical line art from the logo.
- Trust signals up front: RN since 2010, Montfort Hospital, small classes, support person included, insurance coverage.
- One clear primary action everywhere: **Book a class**.
- Inclusive, warm language ("you and your support person").
- Typography: *Cormorant Garamond* (headings, elegant/soft) + *Nunito Sans* (body, rounded, highly legible). Body ≥ 17px, line-height ~1.7.
- Mobile-first: many visitors browse on phones, sometimes late at night — fast, readable, thumb-friendly (tap targets ≥ 44px).

### Palette — zen / holistic
Evolved from the original brand palette (`birthingwithinsight_colour_pallet.jpeg`): sage and stone lead, blush/pink retired, clay kept as a quiet accent. Tokens live at the top of `src/assets/css/site.css`.
| Token | Hex | Use |
|---|---|---|
| `--linen` | `#F4F1EA` | page background |
| `--card` | `#FBFAF6` | cards, raised surfaces |
| `--stone` | `#E9E6DC` | soft section backgrounds, active nav |
| `--sand-soft` | `#EEE8DC` | alternate section background |
| `--sage-soft` | `#E2E7DC` | sage section background, tags |
| `--sage` / `--deep-sage` | `#A9B59E` / `#71816F` | decoration, borders, focus rings — not small text |
| `--sage-ink` | `#5B6A58` | small sage text (eyebrows, meta) |
| `--primary` (moss) | `#4A5A48` | buttons, links, logo line art |
| `--primary-dark` | `#3B4939` | hover, footer background |
| `--heading` | `#3F4A3D` | headings |
| `--charcoal` | `#3A3D39` | body text |
| `--accent` (clay) | `#9A6A55` | large numerals / tiny highlights only |

Accessibility: WCAG AA contrast for all text. Light palette colours are backgrounds/decoration only — never text colour on cream.

## Project layout
```
build.py                  # static site generator (stdlib)
content/blog/{en,fr}/     # blog posts (markdown + front matter)
src/pages/{en,fr}/*.html  # page bodies (HTML fragments with front matter)
src/assets/               # css, js, img  (copied to docs/assets)
docs/                     # BUILD OUTPUT — published by GitHub Pages
tools/                    # one-off helper scripts
.claude/agents/           # site-tester subagent
```

## Workflow
- Build: `python3 build.py` · Preview: `python3 -m http.server 8000 -d docs`
- After changes, run the **site-tester** agent to verify (links, images, both languages, mobile, contrast).

## Open questions for the owner
- Formspree form ID (or keep contact-by-email only).
- Confirm French translations marked for review.
- Custom domain DNS: point `birthingwithinsight.ca` to GitHub Pages when ready to switch from Wix.
