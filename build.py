#!/usr/bin/env python3
"""Static site generator for Birthing With Insight.

Python 3 stdlib only. Reads src/ and content/, writes the finished site to docs/.
Usage:  python3 build.py
"""
import datetime
import html
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
SRC, CONTENT, OUT = ROOT / 'src', ROOT / 'content', ROOT / 'docs'

# ---------------------------------------------------------------- configuration
SITE_URL = 'https://www.birthingwithinsight.ca'
# Path prefix when served from https://<user>.github.io/<repo>/ before the custom
# domain is live, e.g. BASE = '/birthingwithinsight'. Leave '' for the custom domain.
BASE = ''  # live on www.birthingwithinsight.ca; use '/birthingwithinsight' only to test on cedyced.github.io
CNAME = 'www.birthingwithinsight.ca'

# cal.com booking. Leave 'username' empty to show the "book by email/phone" fallback.
CAL = {
    'username': 'ashley-burgins-ya1eov',
    'brand': '#4A5A48',
}
# Formspree form id (e.g. 'xyzabcd'). Empty = no form, contact details only.
FORMSPREE_ID = ''

BUSINESS = {
    'name': 'Birthing With Insight',
    'phone': '1-343-348-9883',
    'phone_href': 'tel:+13433489883',
    'email': 'registration@birthingwithinsight.ca',
    'street': '4289 Innes Road, 2nd floor',
    'city': 'Orléans', 'region': 'ON', 'postal': 'K1E 0A8', 'country': 'CA',
    'map_query': '4289 Innes Road, Orléans, ON K1E 0A8',
}

SERVICES = [
    {
        'id': 'in-person-prenatal-class',
        'legacy': 'in-person-prenatal-class',
        'cal_event': 'in-person-prenatal-class',
        'price': 70, 'image': 'service-en.jpg', 'taught': 'en',
        'en': {
            'name': 'In-Person Prenatal Class',
            'duration': '2.5-hour session',
            'summary': 'A small, hands-on birth preparation class for you and your support person. One fee covers you both.',
            'body': [
                'Our birth preparation sessions are designed for expectant mothers and their chosen support person, in a warm, supportive space for learning about the birthing process.',
                'Learn what to expect through each stage of labour, from the early signs of labour through birth and recovery. We’ll discuss how to recognize when it’s time to go to the hospital, what happens as labour progresses, and practical ways your support person can help you feel informed, confident, and supported throughout the process.',
                'We’ll also explore both medicated and unmedicated pain-management options, helping you understand the choices available so you can make informed decisions about your care.',
                'This interactive session combines essential education with hands-on techniques, including massage, counter-pressure, positioning, and other comfort measures. Together, you and your support person will gain practical tools to navigate labour and delivery as a team and feel prepared for the journey ahead.',
            ],
        },
        'fr': {  # FR: review — translated from the English service description
            'name': 'Cours prénatal en présentiel (en anglais)',
            'duration': 'Séance de 2,5 heures',
            'summary': "Un cours de préparation à l'accouchement en petit groupe, pratique, pour vous et votre personne de soutien. Un seul tarif pour vous deux.",
            'body': [
                'Nos séances de préparation à l’accouchement sont conçues pour les futures mamans et leur personne de soutien, dans un espace chaleureux et bienveillant pour apprendre le déroulement de l’accouchement. Ce cours est donné en anglais.',
                'Découvrez à quoi vous attendre à chaque étape du travail, des premiers signes jusqu’à la naissance et au rétablissement. Nous verrons comment reconnaître le moment de partir pour l’hôpital, ce qui se passe à mesure que le travail progresse, et des façons concrètes dont votre personne de soutien peut vous aider à vous sentir informée, confiante et soutenue tout au long du processus.',
                'Nous explorerons aussi les options de gestion de la douleur, avec ou sans médication, pour vous aider à comprendre les choix qui s’offrent à vous et à prendre des décisions éclairées au sujet de vos soins.',
                'Cette séance interactive allie l’enseignement essentiel à des techniques pratiques : massage, contre-pression, positions et autres mesures de confort. Ensemble, vous et votre personne de soutien repartirez avec des outils concrets pour vivre le travail et l’accouchement en équipe et vous sentir prêts pour l’aventure qui vous attend.',
            ],
        },
    },
    {
        'id': 'cours-prenatal-en-presentiel',
        'legacy': 'cours-prénatal-en-présentiel-1',
        'cal_event': 'cours-prenatal-en-presentiel',
        'price': 70, 'image': 'service-fr.jpg', 'taught': 'fr',
        'en': {  # translated from the French description
            'name': 'In-Person Prenatal Class (French)',
            'duration': '2.5-hour session',
            'summary': 'Our birth preparation class, taught in French. The fee covers the mother-to-be and her support person.',
            'body': [
                'Our birth preparation sessions are designed for expectant mothers and their chosen support person, creating a supportive environment for learning about the birthing process — taught entirely in French.',
                'Learn what to expect through each stage of labour, from the early signs of labour through birth and recovery. We’ll discuss how to recognize when it’s time to go to the hospital, what happens as labour progresses, and practical ways your support person can help you feel informed, confident, and supported throughout the process.',
                'We’ll also explore both medicated and unmedicated pain-management options, helping you understand the choices available so you can make informed decisions about your care.',
                'This interactive session combines essential education with hands-on techniques, including massage, counter-pressure, positioning, and other comfort measures. Together, you and your support person will gain practical tools to navigate labour as a team and feel prepared for the journey ahead.',
            ],
        },
        'fr': {
            'name': 'Cours prénatal en présentiel',
            'duration': 'Séance de 2,5 heures',
            'summary': "Le tarif s'applique à deux participants : la future mère et sa personne de soutien.",
            'body': [
                'Nos séances de préparation à l’accouchement sont conçues pour les futures mamans et leur personne de soutien, dans un environnement bienveillant pour apprendre le déroulement de l’accouchement — entièrement en français.',
                'Découvrez à quoi vous attendre à chaque étape du travail, des premiers signes jusqu’à la naissance et au rétablissement. Nous verrons comment reconnaître le moment de partir pour l’hôpital, ce qui se passe à mesure que le travail progresse, et des façons concrètes dont votre personne de soutien peut vous aider à vous sentir informée, confiante et soutenue tout au long du processus.',
                'Nous explorerons aussi les options de gestion de la douleur, avec ou sans médication, pour vous aider à comprendre les choix qui s’offrent à vous et à prendre des décisions éclairées au sujet de vos soins.',
                'Cette séance interactive allie l’enseignement essentiel à des techniques pratiques : massage, contre-pression, positions et autres mesures de confort. Ensemble, vous et votre personne de soutien repartirez avec des outils concrets pour vivre le travail en équipe et vous sentir prêts pour l’aventure qui vous attend.',
            ],
        },
    },
    {
        'id': 'full-day-prenatal-newborn-care',
        'legacy': 'full-day-prenatal-newborn-care',
        'cal_event': 'full-day-prenatal',
        'price': 150, 'image': 'service-fullday.jpg', 'taught': None,
        'en': {
            'name': 'Full Day Prenatal & Newborn Care',
            'duration': 'Full day · 9 a.m. – 4 p.m.',
            'summary': 'Led by our Registered Nurse and a Certified Lactation Consultant. Covered by most insurance companies.',
            'body': [
                '## Morning — Maternal wellness & recovery',
                'Learn what to expect as your body recovers after delivery, including common physical and emotional changes during the postpartum period. We’ll discuss healing after both vaginal birth and caesarean birth, postpartum bleeding, discomfort, rest, mobility, and the importance of recognizing when additional support or medical care may be needed.',
                'This session also focuses on the vital role of your partner or support person during recovery. Together, you’ll explore practical ways they can support your healing.',
                '## Morning — Newborn care',
                'Build confidence in caring for your newborn with practical guidance on hygiene, safety, and everyday wellbeing. We’ll explore simple ways to keep your baby comfortable, create a safe environment, and recognize signs that may require additional support or medical care.',
                'With a special focus on breastfeeding, this session will be led by a certified lactation consultant who will offer practical support with feeding positions and breastfeeding techniques. We’ll also discuss common breastfeeding challenges and helpful troubleshooting, including strategies to use before baby comes, so you and your baby can get off to a smoother start. Guidance on bottle-feeding is also included, helping you feel confident with the feeding approach that works best for your family.',
                'We’ll also look at why babies cry and practise gentle, effective soothing techniques. You’ll leave feeling better prepared to respond calmly, confidently, and compassionately when your baby needs comfort.',
                'Through open discussion and practical guidance, you’ll gain a clearer understanding of the recovery process and the tools to support maternal well-being and baby as you transition into parenthood.',
                '*After a 45-minute lunch break, we come back together for the labour and delivery session.*',
                '## Afternoon — Labour & delivery',
                'This session is also taught as its own class — [see all classes](/classes/).',
                'Learn what to expect through each stage of labour, from the early signs of labour through birth and recovery. We’ll discuss how to recognize when it’s time to go to the hospital, what happens as labour progresses, and practical ways your support person can help you feel informed, confident, and supported throughout the process.',
                'We’ll also explore both medicated and unmedicated pain-management options, helping you understand the choices available so you can make informed decisions about your care.',
                'This interactive session combines essential education with hands-on techniques, including massage, counter-pressure, positioning, and other comfort measures. Together, you and your support person will gain practical tools to navigate labour as a team and feel prepared for the journey ahead.',
            ],
        },
        'fr': {  # FR: review — translated from the English service description
            'name': 'Journée complète : prénatal et soins du nouveau-né',
            'duration': 'Journée complète · 9 h à 16 h',
            'summary': "Animée par notre infirmière autorisée et une consultante en lactation certifiée. Couverte par la plupart des assurances.",
            'body': [
                '## Matin — Bien-être maternel et rétablissement',
                'Découvrez à quoi vous attendre pendant que votre corps se rétablit après l’accouchement, y compris les changements physiques et émotionnels courants de la période post-partum. Nous aborderons la guérison après un accouchement vaginal et après une césarienne, les saignements post-partum, l’inconfort, le repos, la mobilité, et l’importance de reconnaître quand un soutien supplémentaire ou des soins médicaux peuvent être nécessaires.',
                'Cette séance met aussi l’accent sur le rôle essentiel de votre partenaire ou personne de soutien pendant le rétablissement. Ensemble, vous explorerez des façons concrètes dont elle peut soutenir votre guérison.',
                '## Matin — Soins du nouveau-né',
                'Prenez confiance dans les soins à votre nouveau-né grâce à des conseils pratiques sur l’hygiène, la sécurité et le bien-être au quotidien. Nous verrons des façons simples de garder votre bébé confortable, de créer un environnement sécuritaire et de reconnaître les signes qui peuvent nécessiter un soutien supplémentaire ou des soins médicaux.',
                'Avec une attention particulière à l’allaitement, cette partie est animée par une consultante en lactation certifiée, qui vous offrira un soutien pratique sur les positions et les techniques d’allaitement. Nous aborderons aussi les difficultés courantes et des pistes de solution, y compris des stratégies à mettre en place avant l’arrivée de bébé, pour que vous et votre bébé preniez un départ plus en douceur. Des conseils sur l’alimentation au biberon sont aussi inclus, pour vous aider à vous sentir en confiance avec l’approche qui convient le mieux à votre famille.',
                'Nous verrons également pourquoi les bébés pleurent et pratiquerons des techniques d’apaisement douces et efficaces. Vous repartirez mieux préparés à réagir avec calme, confiance et compassion lorsque votre bébé a besoin de réconfort.',
                'Grâce à des échanges ouverts et à des conseils pratiques, vous comprendrez mieux le processus de rétablissement et repartirez avec des outils pour soutenir le bien-être de la mère et du bébé pendant votre transition vers la parentalité.',
                '*Après une pause-dîner de 45 minutes, nous nous retrouvons pour la séance sur le travail et l’accouchement.*',
                '## Après-midi — Travail et accouchement',
                'Cette séance est aussi offerte comme cours distinct — [voir tous les cours](/fr/classes/).',
                'Découvrez à quoi vous attendre à chaque étape du travail, des premiers signes jusqu’à la naissance et au rétablissement. Nous verrons comment reconnaître le moment de partir pour l’hôpital, ce qui se passe à mesure que le travail progresse, et des façons concrètes dont votre personne de soutien peut vous aider à vous sentir informée, confiante et soutenue tout au long du processus.',
                'Nous explorerons aussi les options de gestion de la douleur, avec ou sans médication, pour vous aider à comprendre les choix qui s’offrent à vous et à prendre des décisions éclairées au sujet de vos soins.',
                'Cette séance interactive allie l’enseignement essentiel à des techniques pratiques : massage, contre-pression, positions et autres mesures de confort. Ensemble, vous et votre personne de soutien repartirez avec des outils concrets pour vivre le travail en équipe et vous sentir prêts pour l’aventure qui vous attend.',
            ],
        },
    },
]

# ---------------------------------------------------------------- translations
T = {
    'en': {
        'html_lang': 'en-CA', 'og_locale': 'en_CA', 'prefix': '',
        'nav': [('/', 'Home'), ('/about/', 'About'), ('/classes/', 'Classes'),
                ('/faq/', 'FAQ'), ('/blog/', 'Blog'), ('/contact/', 'Contact')],
        'book': 'Book a class', 'menu': 'Menu', 'switch_label': 'Français', 'switch_short': 'FR',
        'skip': 'Skip to content',
        'tagline': 'Prenatal classes in Orléans, Ottawa',
        'footer_blurb': 'Small, hands-on prenatal classes led by a labour & delivery nurse — for you and your support person.',
        'footer_visit': 'Visit us', 'footer_reach': 'Get in touch', 'footer_explore': 'Explore',
        'rights': 'All rights reserved.',
        'learn_more': 'Learn more', 'book_now': 'Book now', 'per_couple': 'for you + your support person',
        'taught_in': {'en': 'Taught in English', 'fr': 'Taught in French'},
        'read_more': 'Read article', 'back_blog': 'All articles', 'min_read': 'min read',
        'post_cta_title': 'Ready to feel prepared?',
        'post_cta_text': 'Learn these techniques hands-on, with your support person, in a small and welcoming class.',
        'booking_title': 'Choose a date',
        'booking_fallback': "Online booking is being set up. To reserve your spot, just call or email us — we'll gladly help you choose a session.",
        'call': 'Call', 'email': 'Email',
        'cal_direct': 'Calendar not loading?', 'cal_direct_link': 'Book directly on cal.com →',
        'form': {'name': 'Your name', 'email': 'Email', 'subject': 'Subject', 'message': 'Message',
                 'due': 'Due date (optional)', 'send': 'Send message'},
        'lang_note': '',
        'date_fmt': lambda d: d.strftime('%B %-d, %Y'),
        'not_found': 'Page not found',
    },
    'fr': {
        'html_lang': 'fr-CA', 'og_locale': 'fr_CA', 'prefix': '/fr',
        'nav': [('/fr/', 'Accueil'), ('/fr/about/', 'À propos'), ('/fr/classes/', 'Cours'),
                ('/fr/faq/', 'FAQ'), ('/fr/blog/', 'Blogue'), ('/fr/contact/', 'Contact')],
        'book': 'Réserver un cours', 'menu': 'Menu', 'switch_label': 'English', 'switch_short': 'EN',
        'skip': 'Aller au contenu',
        'tagline': 'Cours prénatals à Orléans, Ottawa',
        'footer_blurb': "Des cours prénatals pratiques, en petit groupe, animés par une infirmière en salle d'accouchement — pour vous et votre personne de soutien.",
        'footer_visit': 'Nous trouver', 'footer_reach': 'Nous joindre', 'footer_explore': 'Explorer',
        'rights': 'Tous droits réservés.',
        'learn_more': 'En savoir plus', 'book_now': 'Réserver', 'per_couple': 'pour vous + votre personne de soutien',
        'taught_in': {'en': 'Offert en anglais', 'fr': 'Offert en français'},
        'read_more': "Lire l'article", 'back_blog': 'Tous les articles', 'min_read': 'min de lecture',
        'post_cta_title': 'Prête à vous sentir préparée ?',
        'post_cta_text': 'Apprenez ces techniques en pratique, avec votre personne de soutien, dans un petit groupe accueillant.',
        'booking_title': 'Choisissez une date',
        'booking_fallback': "La réservation en ligne est en cours de mise en place. Pour réserver votre place, appelez-nous ou écrivez-nous — nous vous aiderons avec plaisir à choisir une séance.",
        'call': 'Appeler', 'email': 'Courriel',
        'cal_direct': 'Le calendrier ne s’affiche pas ?', 'cal_direct_link': 'Réservez directement sur cal.com →',
        'form': {'name': 'Votre nom', 'email': 'Courriel', 'subject': 'Sujet', 'message': 'Message',
                 'due': "Date prévue d'accouchement (facultatif)", 'send': 'Envoyer'},
        'lang_note': '(en anglais)',
        'date_fmt': lambda d: f"{d.day} {['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'][d.month-1]} {d.year}",
        'not_found': 'Page introuvable',
    },
}

# ---------------------------------------------------------------- helpers
esc = html.escape
ASSET_VERSION = datetime.datetime.now().strftime('%Y%m%d%H%M')


def parse_front_matter(text):
    meta = {}
    if text.startswith('---\n'):
        head, text = text[4:].split('\n---\n', 1)
        for line in head.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                meta[k.strip()] = v.strip()
    return meta, text.lstrip('\n')


def inline_md(s):
    s = esc(s, quote=False)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    s = re.sub(r'(?<!\*)\*(?!\s)(.+?)\*', r'<em>\1</em>', s)
    s = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', s)
    return s


def markdown(text):
    """Tiny markdown: headings, paragraphs, bullet lists, numbered paragraphs → <ol>."""
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text) if b.strip()]
    out, i = [], 0
    while i < len(blocks):
        b = blocks[i]
        m = re.match(r'(#{1,4})\s+(.*)', b)
        if m:
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f'<h{lvl}>{inline_md(m.group(2))}</h{lvl}>')
        elif re.match(r'\d+\.\s', b):
            start = int(re.match(r'(\d+)', b).group(1))
            items = []
            while i < len(blocks) and re.match(r'\d+\.\s', blocks[i]):
                for line in re.split(r'\n(?=\d+\.\s)', blocks[i]):
                    body = re.sub(r'^\d+\.\s+', '', line)
                    # "Label: explanation" → bold the short label
                    lm = re.match(r'([^:]{3,60}):\s+(.*)', body, re.S)
                    items.append(f'<li><strong>{inline_md(lm.group(1))}:</strong> {inline_md(lm.group(2))}</li>'
                                 if lm else f'<li>{inline_md(body)}</li>')
                i += 1
            attr = f' start="{start}"' if start != 1 else ''
            out.append(f'<ol{attr}>' + ''.join(items) + '</ol>')
            continue
        elif b.startswith('- '):
            items = [inline_md(l[2:]) for l in b.splitlines() if l.startswith('- ')]
            out.append('<ul>' + ''.join(f'<li>{x}</li>' for x in items) + '</ul>')
        else:
            out.append(f'<p>{inline_md(b)}</p>')
        i += 1
    return '\n'.join(out)



def svc_url(lang, s):
    return f"{T[lang]['prefix']}/classes/{s['id']}/"


def cal_link(s):
    return f"{CAL['username']}/{s['cal_event']}" if CAL['username'] else ''


def price(lang, n):
    return f'${n}' if lang == 'en' else f'{n} $'


# ---------------------------------------------------------------- components
def c_service_cards(lang, heading_level=3):
    t, cards = T[lang], []
    for s in SERVICES:
        d = s[lang]
        tag = f'<span class="tag tag--{s["taught"]}">{t["taught_in"][s["taught"]]}</span>' if s['taught'] else \
              f'<span class="tag tag--ins">{"Insurance eligible" if lang == "en" else "Admissible à l’assurance"}</span>'
        book = (f'<a class="btn btn--primary btn--sm" href="https://cal.com/{cal_link(s)}" data-cal-popup="{cal_link(s)}">{t["book_now"]}</a>'
                if CAL['username'] else
                f'<a class="btn btn--primary btn--sm" href="{svc_url(lang, s)}#book">{t["book_now"]}</a>')
        cards.append(f'''
      <article class="class-card reveal">
        <a class="class-card__media" href="{svc_url(lang, s)}" tabindex="-1" aria-hidden="true">
          <img src="/assets/img/{s["image"]}" alt="" loading="lazy" width="1200" height="800">
        </a>
        <div class="class-card__body">
          {tag}
          <h{heading_level} class="class-card__title"><a href="{svc_url(lang, s)}">{esc(d["name"])}</a></h{heading_level}>
          <p class="class-card__meta">{esc(d["duration"])}</p>
          <p>{esc(d["summary"])}</p>
          <div class="class-card__foot">
            <p class="price"><span class="price__num">{price(lang, s["price"])}</span> <span class="price__note">{t["per_couple"]}</span></p>
            <div class="class-card__actions">
              <a class="btn btn--ghost btn--sm" href="{svc_url(lang, s)}">{t["learn_more"]}</a>
              {book}
            </div>
          </div>
        </div>
      </article>''')
    return '<div class="class-grid">' + ''.join(cards) + '\n    </div>'


def c_booking(lang, s=None):
    t = T[lang]
    if not CAL['username']:
        return f'''
    <div class="booking-fallback">
      <img src="/assets/img/logo-mark.png" alt="" width="140" height="68">
      <p>{t["booking_fallback"]}</p>
      <div class="btn-row">
        <a class="btn btn--primary" href="{BUSINESS["phone_href"]}">{t["call"]} {BUSINESS["phone"]}</a>
        <a class="btn btn--ghost" href="mailto:{BUSINESS["email"]}">{BUSINESS["email"]}</a>
      </div>
    </div>'''
    link = cal_link(s) if s else CAL['username']
    return f'''
    <div class="cal-embed" id="cal-inline" data-cal-inline="{link}"></div>
    <p class="cal-direct">{t["cal_direct"]} <a href="https://cal.com/{link}" rel="noopener">{t["cal_direct_link"]}</a></p>'''


def c_latest_posts(lang, n=3, posts=None):
    if posts is None:  # French pages also show English posts (only one French post exists)
        posts = POSTS_BY_LANG[lang] + (POSTS_BY_LANG['en'] if lang == 'fr' else [])
    items = posts[:n]
    return '<div class="post-grid">' + ''.join(post_card(lang, p) for p in items) + '</div>'


def c_contact_form(lang):
    if not FORMSPREE_ID:
        return ''
    f = T[lang]['form']
    return f'''
    <form class="contact-form" action="https://formspree.io/f/{FORMSPREE_ID}" method="POST">
      <div class="field"><label for="cf-name">{f["name"]}</label><input id="cf-name" name="name" autocomplete="name" required></div>
      <div class="field"><label for="cf-email">{f["email"]}</label><input id="cf-email" name="email" type="email" autocomplete="email" required></div>
      <div class="field"><label for="cf-due">{f["due"]}</label><input id="cf-due" name="due_date" type="date"></div>
      <div class="field"><label for="cf-subject">{f["subject"]}</label><input id="cf-subject" name="subject"></div>
      <div class="field field--full"><label for="cf-msg">{f["message"]}</label><textarea id="cf-msg" name="message" rows="5" required></textarea></div>
      <button class="btn btn--primary" type="submit">{f["send"]}</button>
    </form>'''


def c_map(lang):
    q = BUSINESS['map_query'].replace(' ', '+')
    title = 'Map to 4289 Innes Road, Orléans' if lang == 'en' else 'Carte : 4289, chemin Innes, Orléans'
    return (f'<iframe class="map" title="{title}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" '
            f'src="https://maps.google.com/maps?q={q}&amp;z=15&amp;output=embed"></iframe>')


COMPONENTS = {
    'service_cards': c_service_cards,
    'booking': c_booking,
    'latest_posts': c_latest_posts,
    'contact_form': c_contact_form,
    'map': c_map,
}

# ---------------------------------------------------------------- layout
def header(lang, alt_path, current):
    t = T[lang]
    links = ''.join(
        f'<li><a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a></li>'
        for href, label in t['nav'])
    other = 'fr' if lang == 'en' else 'en'
    return f'''
<a class="skip-link" href="#main">{t["skip"]}</a>
<header class="site-header">
  <div class="container site-header__inner">
    <a class="brand" href="{t["nav"][0][0]}" aria-label="{BUSINESS["name"]} — {t["nav"][0][1]}">
      <img class="brand__mark" src="/assets/img/logo-mark.png" alt="" width="203" height="98">
      <span class="brand__text"><span class="brand__name">Birthing With Insight</span></span>
    </a>
    <button class="nav-toggle" aria-expanded="false" aria-controls="site-nav">
      <span class="nav-toggle__bars" aria-hidden="true"></span><span class="nav-toggle__label">{t["menu"]}</span>
    </button>
    <nav class="site-nav" id="site-nav" aria-label="Main">
      <ul>{links}</ul>
      <div class="site-nav__actions">
        <a class="lang-switch" href="{alt_path}" hreflang="{other}" lang="{other}" aria-label="{t["switch_label"]}">{t["switch_short"]}</a>
        <a class="btn btn--primary btn--sm" href="{t["prefix"]}/classes/">{t["book"]}</a>
      </div>
    </nav>
  </div>
</header>'''


def footer(lang):
    t = T[lang]
    b = BUSINESS
    nav = ''.join(f'<li><a href="{h}">{l}</a></li>' for h, l in t['nav'][1:])
    year = datetime.date.today().year
    return f'''
<footer class="site-footer">
  <div class="container site-footer__grid">
    <div class="site-footer__brand">
      <img src="/assets/img/logo-mark-light.png" alt="" width="160" height="77">
      <p class="site-footer__name">{b["name"]}</p>
      <p>{t["footer_blurb"]}</p>
    </div>
    <div>
      <h2 class="site-footer__h">{t["footer_visit"]}</h2>
      <address>Ottawa Medical Group<br>{b["street"]}<br>{b["city"]}, {b["region"]} {b["postal"]}</address>
    </div>
    <div>
      <h2 class="site-footer__h">{t["footer_reach"]}</h2>
      <p><a href="{b["phone_href"]}">{b["phone"]}</a><br><a href="mailto:{b["email"]}">{b["email"]}</a></p>
    </div>
    <div>
      <h2 class="site-footer__h">{t["footer_explore"]}</h2>
      <ul class="site-footer__nav">{nav}</ul>
    </div>
  </div>
  <div class="container site-footer__legal">
    <p>© {year} {b["name"]} Inc. {t["rights"]}</p>
  </div>
</footer>'''


def cal_script(lang):
    if not CAL['username']:
        return ''
    ui = json.dumps({'cssVarsPerTheme': {'light': {'cal-brand': CAL['brand']}},
                     'hideEventTypeDetails': False, 'layout': 'month_view', 'theme': 'light'})
    return f'''
<script>
(function (C, A, L) {{ let p = function (a, ar) {{ a.q.push(ar); }}; let d = C.document; C.Cal = C.Cal || function () {{ let cal = C.Cal; let ar = arguments; if (!cal.loaded) {{ cal.ns = {{}}; cal.q = cal.q || []; d.head.appendChild(d.createElement("script")).src = A; cal.loaded = true; }} if (ar[0] === L) {{ const api = function () {{ p(api, arguments); }}; const namespace = ar[1]; api.q = api.q || []; if (typeof namespace === "string") {{ cal.ns[namespace] = cal.ns[namespace] || api; p(cal.ns[namespace], ar); p(cal, ["initNamespace", namespace]); }} else p(cal, ar); return; }} p(cal, ar); }}; }})(window, "https://app.cal.com/embed/embed.js", "init");
Cal("init", "bwi", {{ origin: "https://cal.com" }});
Cal.ns.bwi("ui", {ui});
var inline = document.querySelector("[data-cal-inline]");
if (inline) Cal.ns.bwi("inline", {{ elementOrSelector: inline, calLink: inline.dataset.calInline, config: {{ layout: "month_view", locale: "{lang}" }} }});
// "Book now" links open a cal.com popup once embed.js has loaded; otherwise they stay plain links to cal.com.
var calReady = false, calScript = document.querySelector('script[src$="/embed/embed.js"]');
if (calScript) calScript.addEventListener("load", function () {{ calReady = true; }});
document.addEventListener("click", function (e) {{
  var a = e.target.closest && e.target.closest("a[data-cal-popup]");
  if (!a || !calReady || e.metaKey || e.ctrlKey || e.shiftKey) return;
  e.preventDefault();
  Cal.ns.bwi("modal", {{ calLink: a.dataset.calPopup, config: {{ layout: "month_view", locale: "{lang}" }} }});
}});
</script>'''


def page(lang, *, title, description, path, alt_path, body, image=None, body_class='',
         extra_head='', nav_current=None, noindex=False):
    t = T[lang]
    full_title = title if BUSINESS['name'] in title else f'{title} · {BUSINESS["name"]}'
    en_path, fr_path = (path, alt_path) if lang == 'en' else (alt_path, path)
    og_img = f'{SITE_URL}/assets/img/{image or "hero-newborn.jpg"}'
    robots = '<meta name="robots" content="noindex">' if noindex else ''
    doc = f'''<!doctype html>
<html lang="{t["html_lang"]}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(full_title)}</title>
<meta name="description" content="{esc(description)}">
{robots}
<link rel="canonical" href="{SITE_URL}{path}">
<link rel="alternate" hreflang="en-CA" href="{SITE_URL}{en_path}">
<link rel="alternate" hreflang="fr-CA" href="{SITE_URL}{fr_path}">
<link rel="alternate" hreflang="x-default" href="{SITE_URL}{en_path}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(BUSINESS["name"])}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{SITE_URL}{path}">
<meta property="og:image" content="{og_img}">
<meta property="og:locale" content="{t["og_locale"]}">
<meta name="twitter:card" content="summary_large_image">
<meta name="theme-color" content="#F4F1EA">
<link rel="icon" href="/assets/img/favicon.svg" type="image/svg+xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;1,500&family=Nunito+Sans:ital,opsz,wght@0,6..12,400;0,6..12,600;0,6..12,700;1,6..12,400&display=swap">
<link rel="stylesheet" href="/assets/css/site.css?v={ASSET_VERSION}">
{extra_head}
</head>
<body class="{body_class}">
{header(lang, alt_path, nav_current or path)}
<main id="main">
{body}
</main>
{footer(lang)}
<script src="/assets/js/site.js?v={ASSET_VERSION}" defer></script>
{cal_script(lang)}
</body>
</html>
'''
    return doc


def write(path, doc):
    """path is a site path like /about/ or /404.html"""
    if BASE:
        doc = re.sub(r'(href|src)="/(?!/)', rf'\1="{BASE}/', doc)
    target = OUT / (path.lstrip('/') + ('index.html' if path.endswith('/') else ''))
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(doc)
    SITEMAP.append(path) if 'noindex' not in doc[:3000] and 'http-equiv="refresh"' not in doc else None


def redirect(from_path, to_path):
    doc = f'''<!doctype html><html><head><meta charset="utf-8"><title>Redirecting…</title>
<link rel="canonical" href="{SITE_URL}{to_path}"><meta name="robots" content="noindex">
<meta http-equiv="refresh" content="0; url={to_path}"></head>
<body><p><a href="{to_path}">Continue →</a></p></body></html>'''
    write(from_path, doc)


# ---------------------------------------------------------------- blog
POSTS_BY_LANG = {'en': [], 'fr': []}


def load_posts():
    for lang in ('en', 'fr'):
        for f in sorted((CONTENT / 'blog' / lang).glob('*.md')):
            meta, body = parse_front_matter(f.read_text())
            meta['slug'] = f.stem
            meta['lang'] = lang
            meta['body'] = body
            meta['date_obj'] = datetime.date.fromisoformat(meta['date'])
            meta['minutes'] = max(1, round(len(body.split()) / 200))
            POSTS_BY_LANG[lang].append(meta)
        POSTS_BY_LANG[lang].sort(key=lambda p: (p['date_obj'], p['title']), reverse=True)


def post_url(p):
    return f"{T[p['lang']]['prefix']}/post/{p['slug']}/"


def post_card(lang, p):
    t = T[lang]
    note = f' <span class="lang-note">{t["lang_note"]}</span>' if p['lang'] != lang and t['lang_note'] else ''
    hreflang = f' hreflang="{p["lang"]}"' if p['lang'] != lang else ''
    return f'''
      <article class="post-card reveal">
        <a class="post-card__media" href="{post_url(p)}" tabindex="-1" aria-hidden="true"><img src="/assets/img/{p["image"]}" alt="" loading="lazy" width="1200" height="800"></a>
        <div class="post-card__body">
          <p class="post-card__meta">{p["minutes"]} {t["min_read"]}</p>
          <h3 class="post-card__title"><a href="{post_url(p)}"{hreflang}>{esc(p["title"])}</a>{note}</h3>
          <p>{esc(p["excerpt"])}</p>
        </div>
      </article>'''


def build_blog():
    # Blog index per language. FR index lists French posts first, then English ones.
    for lang in ('en', 'fr'):
        t = T[lang]
        posts = POSTS_BY_LANG[lang] + (POSTS_BY_LANG['en'] if lang == 'fr' else [])
        intro = ('Gentle, practical reading for pregnancy, birth and the early weeks with your baby.'
                 if lang == 'en' else
                 "Des lectures douces et pratiques pour la grossesse, l'accouchement et les premières semaines avec bébé.")
        heading = 'The Blog' if lang == 'en' else 'Le blogue'
        body = f'''
<section class="page-hero page-hero--compact">
  <div class="container narrow">
    <p class="eyebrow">{"Articles & insight" if lang == "en" else "Articles et conseils"}</p>
    <h1>{heading}</h1>
    <p class="lede">{intro}</p>
  </div>
</section>
<section class="section section--tight">
  <div class="container">
    <div class="post-grid">{"".join(post_card(lang, p) for p in posts)}</div>
  </div>
</section>'''
        path = f'{t["prefix"]}/blog/'
        alt = f'{T["fr" if lang == "en" else "en"]["prefix"]}/blog/'
        write(path, page(lang, title=heading, description=intro, path=path, alt_path=alt, body=body))

    fr_pair = {'preparation-pour-une-experience-de-naissance-positive': 'preparing-for-a-positive-birth-experience'}
    en_pair = {v: k for k, v in fr_pair.items()}
    for lang in ('en', 'fr'):
        t = T[lang]
        for idx, p in enumerate(POSTS_BY_LANG[lang]):
            if lang == 'en':
                alt = f'/fr/post/{en_pair[p["slug"]]}/' if p['slug'] in en_pair else '/fr/blog/'
            else:
                alt = f'/post/{fr_pair[p["slug"]]}/' if p['slug'] in fr_pair else '/blog/'
            others = [q for q in POSTS_BY_LANG['en' if lang == 'en' else 'en'] if q['slug'] != p['slug']
                      and q['slug'] != fr_pair.get(p['slug'])][:3]
            body = f'''
<article class="post">
  <header class="post__header">
    <div class="container narrow">
      <a class="back-link" href="{t["prefix"]}/blog/">← {t["back_blog"]}</a>
      <h1>{esc(p["title"])}</h1>
      <p class="post__meta"><time datetime="{p["date"]}">{t["date_fmt"](p["date_obj"])}</time> · {p["minutes"]} {t["min_read"]}</p>
    </div>
  </header>
  <figure class="post__hero container">
    <img src="/assets/img/{p["image"]}" alt="" width="1200" height="800">
  </figure>
  <div class="container narrow prose">
{markdown(p["body"])}
  </div>
</article>
<section class="section">
  <div class="container narrow">
    <div class="cta-card">
      <img src="/assets/img/logo-mark.png" alt="" width="140" height="68">
      <h2>{t["post_cta_title"]}</h2>
      <p>{t["post_cta_text"]}</p>
      <a class="btn btn--primary" href="{t["prefix"]}/classes/">{t["book"]}</a>
    </div>
  </div>
</section>
<section class="section section--soft">
  <div class="container">
    <h2 class="section-title">{"Keep reading" if lang == "en" else "À lire aussi"}</h2>
    {c_latest_posts(lang, 3, others)}
  </div>
</section>'''
            ld = json.dumps({
                '@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': p['title'],
                'datePublished': p['date'], 'image': f'{SITE_URL}/assets/img/{p["image"]}',
                'author': {'@type': 'Person', 'name': 'Ashley'},
                'publisher': {'@type': 'Organization', 'name': BUSINESS['name']},
                'inLanguage': t['html_lang'],
            }, ensure_ascii=False)
            write(post_url(p), page(lang, title=p['title'], description=p['excerpt'], path=post_url(p),
                                    alt_path=alt, body=body, image=p['image'],
                                    nav_current=f'{t["prefix"]}/blog/',
                                    extra_head=f'<script type="application/ld+json">{ld}</script>'))


# ---------------------------------------------------------------- services
def build_services():
    for lang in ('en', 'fr'):
        t = T[lang]
        other = 'fr' if lang == 'en' else 'en'
        for s in SERVICES:
            d = s[lang]
            tag = f'<span class="tag tag--{s["taught"]}">{t["taught_in"][s["taught"]]}</span>' if s['taught'] else ''
            facts_en = [('Duration', d['duration']), ('Price', f'{price(lang, s["price"])} — {t["per_couple"]}'),
                        ('Where', 'Ottawa Medical Group, 4289 Innes Rd, 2nd floor, Orléans'),
                        ('Best timing', 'Between 25 and 35 weeks (all welcome)')]
            facts_fr = [('Durée', d['duration']), ('Tarif', f'{price(lang, s["price"])} — {t["per_couple"]}'),
                        ('Lieu', "Groupe médical d'Ottawa, 4289, chemin Innes, 2e étage, Orléans"),
                        ('Moment idéal', 'Entre 25 et 35 semaines (tout le monde est bienvenu)')]
            body_html = markdown('\n\n'.join(d['body']))  # supports ## subheadings, *italic*, [links](/x/)
            facts = ''.join(f'<div><dt>{k}</dt><dd>{v}</dd></div>' for k, v in (facts_en if lang == 'en' else facts_fr))
            body = f'''
<section class="page-hero page-hero--service">
  <div class="container service-hero">
    <div class="service-hero__text">
      <a class="back-link" href="{t["prefix"]}/classes/">← {"All classes" if lang == "en" else "Tous les cours"}</a>
      {tag}
      <h1>{esc(d["name"])}</h1>
      <p class="lede">{esc(d["summary"])}</p>
      <a class="btn btn--primary" href="#book">{t["book_now"]}</a>
    </div>
    <div class="service-hero__media blob-frame">
      <img src="/assets/img/{s["image"]}" alt="" width="1200" height="800">
    </div>
  </div>
</section>
<section class="section section--tight">
  <div class="container service-detail">
    <div class="prose">
      <h2>{"About this class" if lang == "en" else "À propos de ce cours"}</h2>
      {body_html}
    </div>
    <aside class="fact-card" aria-label="{"Class details" if lang == "en" else "Détails du cours"}">
      <dl>{facts}</dl>
    </aside>
  </div>
</section>
<section class="section section--blush" id="book">
  <div class="container">
    <h2 class="section-title">{t["booking_title"]}</h2>
    {c_booking(lang, s)}
  </div>
</section>'''
            path = svc_url(lang, s)
            write(path, page(lang, title=d['name'], description=d['summary'], path=path,
                             alt_path=svc_url(other, s), body=body, image=s['image'],
                             nav_current=f'{t["prefix"]}/classes/'))
            redirect(f'{t["prefix"]}/service-page/{s["legacy"]}/', path)


# ---------------------------------------------------------------- pages
def render_components(lang, body):
    def sub(m):
        name, *args = m.group(1).split(':')
        return COMPONENTS[name](lang, *[int(a) if a.isdigit() else a for a in args])
    body = re.sub(r'\{\{\s*([\w:]+)\s*\}\}', sub, body)
    body = body.replace('[[phone]]', BUSINESS['phone']).replace('[[phone_href]]', BUSINESS['phone_href'])
    return body.replace('[[email]]', BUSINESS['email'])


def build_pages():
    for lang in ('en', 'fr'):
        for f in sorted((SRC / 'pages' / lang).glob('*.html')):
            meta, body = parse_front_matter(f.read_text())
            extra = ''
            if meta.get('schema') == 'business':
                extra = business_ld(lang)
            write(meta['path'], page(lang, title=meta['title'], description=meta['description'],
                                     path=meta['path'], alt_path=meta['alt'],
                                     body=render_components(lang, body),
                                     image=meta.get('image'), body_class=meta.get('body_class', ''),
                                     extra_head=extra, noindex=meta.get('noindex') == 'true'))


def business_ld(lang):
    b = BUSINESS
    data = {
        '@context': 'https://schema.org', '@type': 'LocalBusiness', 'name': b['name'],
        'url': SITE_URL + T[lang]['prefix'] + '/', 'telephone': b['phone'], 'email': b['email'],
        'image': f'{SITE_URL}/assets/img/hero-newborn.jpg',
        'address': {'@type': 'PostalAddress', 'streetAddress': b['street'], 'addressLocality': b['city'],
                    'addressRegion': b['region'], 'postalCode': b['postal'], 'addressCountry': b['country']},
        'makesOffer': [{'@type': 'Offer', 'price': s['price'], 'priceCurrency': 'CAD',
                        'itemOffered': {'@type': 'Service', 'name': s[lang]['name']}} for s in SERVICES],
    }
    return f'<script type="application/ld+json">{json.dumps(data, ensure_ascii=False)}</script>'


# ---------------------------------------------------------------- main
SITEMAP = []


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(SRC / 'assets', OUT / 'assets')
    load_posts()
    build_pages()
    build_services()
    build_blog()
    # Legacy Wix URLs
    redirect('/book-online/', '/classes/')
    redirect('/fr/book-online/', '/fr/classes/')
    (OUT / '.nojekyll').write_text('')
    if CNAME and not BASE:
        (OUT / 'CNAME').write_text(CNAME + '\n')
    (OUT / 'robots.txt').write_text(f'User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n')
    today = datetime.date.today().isoformat()
    urls = ''.join(f'<url><loc>{SITE_URL}{p}</loc><lastmod>{today}</lastmod></url>\n'
                   for p in sorted(set(SITEMAP)) if p.endswith('/'))
    (OUT / 'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?>\n'
                                     '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                                     f'{urls}</urlset>\n')
    n = len(list(OUT.rglob('*.html')))
    print(f'Built {n} HTML files into {OUT.relative_to(ROOT)}/' + (' (booking: fallback mode)' if not CAL['username'] else ''))


if __name__ == '__main__':
    main()
