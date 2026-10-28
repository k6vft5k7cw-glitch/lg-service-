#!/usr/bin/env python3
"""Génère les pages HTML du site LG Service.

Usage : python3 build.py

Les contenus de chaque page sont dans src/pages/*.html. Ce script ajoute
l'en-tête, le pied de page, les balises SEO (title, description, canonical,
Open Graph, données structurées JSON-LD) puis écrit les pages, le sitemap.xml
et le robots.txt à la racine du dépôt.
"""
import html
import json
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).parent
SRC = ROOT / "src"

# Adresse définitive du site (sert aux balises canonical, au sitemap et à Open Graph).
SITE = "https://www.debarras-lg-service.fr"

BUSINESS = {
    "name": "LG Service",
    "phone": "+33681219360",
    "phone_display": "06 81 21 93 60",
    "email": "contact@debarras-lg-service.fr",
    "street": "Chemin De La Plaine",
    "postal": "01300",
    "city": "Brégnier-Cordon",
    "facebook": "https://facebook.com/p/LG-services-100069107802754/",
}

# Communes situées à moins de 30 km de Morestel.
ZONES = [
    "Morestel", "Brégnier-Cordon", "Les Avenières Veyrins-Thuellin", "Arandon-Passins",
    "Vasselin", "Sermérieu", "Saint-Victor-de-Morestel", "Creys-Mépieu", "Vézeronce-Curtin",
    "Bouvesse-Quirieu", "Courtenay", "Montalieu-Vercieu", "Aoste", "Saint-Genix-les-Villages",
    "La Tour-du-Pin", "Crémieu", "Saint-Chef", "Belley",
]

IMAGES = {  # nom: (largeur, hauteur) de la version pleine taille
    "benne-dechets-verts-morestel": (1600, 758),
    "camion-benne-lg-service": (1600, 758),
    "location-benne-chateau-isere": (954, 960),
    "rachat-cuivre-metaux": (1600, 1064),
    "location-benne-bois-gravats": (1600, 1143),
    "debarras-garage-avant": (1600, 876),
}

FAQ = {
    "accueil": [
        ("Quels services propose LG Service à Morestel ?",
         "LG Service propose la location de bennes de 3 à 12 m³, le débarras de maisons, pièces et locaux professionnels, ainsi que l'achat et la vente de métaux (cuivre, laiton, fils électriques, ferraille, batteries), pour les particuliers et les entreprises."),
        ("Dans quelle zone intervenez-vous ?",
         "Nous intervenons à Morestel et dans les communes alentour : jusqu'à 30 km pour la location de bennes et jusqu'à 50 km pour le débarras."),
        ("Quels sont vos horaires ?",
         "LG Service est joignable 24 heures sur 24, 7 jours sur 7, au 06 81 21 93 60 ou par e-mail à contact@debarras-lg-service.fr."),
        ("Quels moyens de paiement acceptez-vous ?",
         "Nous acceptons les chèques, les espèces et les virements."),
    ],
    "bennes": [
        ("Quelles tailles de bennes proposez-vous ?",
         "Nous louons des bennes de 3 à 12 m³. La capacité est choisie selon le volume et le type de déchets à évacuer."),
        ("Quels déchets peut-on mettre dans une benne ?",
         "Nous mettons à votre disposition des bennes adaptées au type de déchets : déchets industriels, bois, gravats ou ferrailles, ainsi que les encombrants de chantier, de rénovation ou de grand nettoyage."),
        ("Combien coûte la location d'une benne ?",
         "La location est facturée au tonnage. Contactez-nous pour obtenir un devis adapté à votre projet."),
        ("Sous quel délai la benne peut-elle être livrée ?",
         "La livraison est possible dans la journée, sous réserve de disponibilité. La benne est livrée par camion sur le lieu de votre choix, pour la durée qui vous convient."),
        ("Que deviennent les déchets ?",
         "Une fois la benne remplie, nous la récupérons et transportons les déchets vers un centre de tri ou de valorisation."),
    ],
    "debarras": [
        ("Quels lieux pouvez-vous débarrasser ?",
         "Nos artisans prennent en charge l'évacuation de granges, garages, ateliers, maisons, caves et locaux d'entreprise, d'une seule pièce jusqu'au bâtiment entier."),
        ("Intervenez-vous après un décès ou une succession ?",
         "Oui. Nous débarrassons maisons et locaux suite à une succession, à une vente immobilière ou avant un déménagement, pour vous libérer du tri et du transport."),
        ("Comment se déroule un débarras ?",
         "Nous évaluons d'abord le volume à vider et le temps nécessaire, puis nous apportons une ou plusieurs bennes selon l'ampleur du chantier. Une fois le tri terminé, nous emportons déchets, meubles et objets vers des centres de tri et de valorisation."),
        ("Jusqu'où vous déplacez-vous pour un débarras ?",
         "Nous nous déplaçons à Morestel et jusqu'à 50 km alentour."),
    ],
    "metaux": [
        ("Quels métaux rachetez-vous ?",
         "LG Service achète et valorise le cuivre, le laiton, les fils électriques en PVC, la ferraille et les batteries."),
        ("Vendez-vous des métaux recyclés ?",
         "Oui. Une fois récupérés et traités, nous revendons des métaux bruts (cuivre, laiton, fils électriques, ferraille, batteries) aux entreprises de construction, artisans et industriels."),
        ("Comment vendre mes métaux ?",
         "Contactez-nous par téléphone au 06 81 21 93 60 ou par e-mail : nous récupérons et rachetons vos métaux pour leur offrir une seconde vie."),
    ],
}

NAV = [
    ("a-propos/", "À propos"),
    ("location-bennes/", "Location de bennes"),
    ("debarras/", "Débarras"),
    ("vente-metaux/", "Vente de métaux"),
    ("contact/", "Contact"),
]

PAGES = [
    {
        "src": "accueil", "out": "index.html", "path": "",
        "title": "Débarras et location de bennes à Morestel | LG Service",
        "desc": "LG Service : débarras de maisons et locaux, location de bennes de 3 à 12 m³ et achat de métaux à Morestel et 30 km alentour. Ouvert 24h/24 – 06 81 21 93 60.",
        "image": "benne-dechets-verts-morestel", "faq": "accueil", "loader": True,
        "priority": "1.0",
    },
    {
        "src": "location-bennes", "out": "location-bennes/index.html", "path": "location-bennes/",
        "title": "Location de bennes à Morestel (3 à 12 m³) | LG Service",
        "desc": "Location de bennes de 3 à 12 m³ à Morestel et 30 km alentour : déchets industriels, bois, gravats, ferrailles. Livraison possible dans la journée.",
        "image": "location-benne-bois-gravats", "faq": "bennes", "crumb": "Location de bennes",
        "service": ("Location de bennes", "Location de bennes de 3 à 12 m³ pour déchets industriels, bois, gravats et ferrailles, livrées et reprises par camion."),
        "priority": "0.9",
    },
    {
        "src": "debarras", "out": "debarras/index.html", "path": "debarras/",
        "title": "Débarras maison, cave, garage à Morestel | LG Service",
        "desc": "Débarras de maisons, caves, garages, granges et locaux pro à Morestel et 50 km alentour, après décès, succession, vente ou déménagement.",
        "image": "debarras-garage-avant", "faq": "debarras", "crumb": "Débarras",
        "service": ("Débarras", "Débarras de maisons, pièces, caves, garages, granges, ateliers et locaux d'entreprise, avec tri et valorisation."),
        "priority": "0.9",
    },
    {
        "src": "vente-metaux", "out": "vente-metaux/index.html", "path": "vente-metaux/",
        "title": "Achat de métaux à Morestel : cuivre, laiton | LG Service",
        "desc": "LG Service rachète vos métaux à Morestel : cuivre, laiton, fils électriques, ferraille, batteries. Revente de métaux valorisés aux artisans et entreprises.",
        "image": "rachat-cuivre-metaux", "faq": "metaux", "crumb": "Vente de métaux",
        "service": ("Achat et vente de métaux", "Rachat et revente de cuivre, laiton, fils électriques, ferraille et batteries."),
        "priority": "0.8",
    },
    {
        "src": "a-propos", "out": "a-propos/index.html", "path": "a-propos/",
        "title": "À propos – Entreprise de débarras à Morestel | LG Service",
        "desc": "Fondée en 2021, LG Service est une entreprise familiale de débarras, location de bennes, valorisation et vente de métaux à Morestel, en Isère.",
        "image": "location-benne-chateau-isere", "crumb": "À propos", "priority": "0.6",
    },
    {
        "src": "contact", "out": "contact/index.html", "path": "contact/",
        "title": "Contact et devis à Morestel | LG Service",
        "desc": "Contactez LG Service pour un devis de débarras ou de location de bennes à Morestel : 06 81 21 93 60, contact@debarras-lg-service.fr. Ouvert 24h/24, 7j/7.",
        "image": "camion-benne-lg-service", "crumb": "Contact", "priority": "0.7",
    },
    {
        "src": "mentions-legales", "out": "mentions-legales/index.html", "path": "mentions-legales/",
        "title": "Mentions légales | LG Service", "desc": "Mentions légales du site de LG Service, Chemin De La Plaine, 01300 Brégnier-Cordon.",
        "crumb": "Mentions légales", "priority": "0.2",
    },
    {
        "src": "vie-privee", "out": "vie-privee/index.html", "path": "vie-privee/",
        "title": "Vie privée et données personnelles | LG Service", "desc": "Utilisation de vos données personnelles par LG Service et exercice de vos droits.",
        "crumb": "Vie privée", "priority": "0.2",
    },
    {
        "src": "404", "out": "404.html", "path": "404.html", "noindex": True, "flat": True,
        "title": "Page introuvable | LG Service", "desc": "Cette page n'existe pas ou a été déplacée.",
    },
]

ARROW = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
PHONE_ICON = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.6 10.8a15.2 15.2 0 0 0 6.6 6.6l2.2-2.2a1 1 0 0 1 1-.25 11.4 11.4 0 0 0 3.6.57 1 1 0 0 1 1 1V20a1 1 0 0 1-1 1A17 17 0 0 1 3 4a1 1 0 0 1 1-1h3.5a1 1 0 0 1 1 1c0 1.25.2 2.45.57 3.6a1 1 0 0 1-.25 1z"/></svg>'


def esc(s):
    return html.escape(s, quote=True)


def img_tag(root, name, alt, cls="", eager=False):
    w, h = IMAGES[name]
    attrs = f' class="{cls}"' if cls else ""
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    return (f'<img src="{root}assets/img/{name}.webp" '
            f'srcset="{root}assets/img/{name}-800.webp 800w, {root}assets/img/{name}.webp {w}w" '
            f'sizes="(max-width: 900px) 100vw, 50vw" width="{w}" height="{h}" alt="{esc(alt)}"{attrs}{load}>')


def faq_html(key):
    items = "\n".join(
        f'<details class="faq__item reveal-up"><summary><h3>{esc(q)}</h3><span class="faq__icon" aria-hidden="true"></span></summary>'
        f'<div class="faq__a"><p>{esc(a)}</p></div></details>' for q, a in FAQ[key])
    return f'''<section class="faq container" aria-labelledby="faq-title">
  <div class="section-head">
    <p class="kicker reveal-up">Questions fréquentes</p>
    <h2 id="faq-title" class="split">Vos questions, nos réponses</h2>
  </div>
  <div class="faq__list">
{items}
  </div>
</section>'''


def zones_html():
    lis = "".join(f"<li>{esc(z)}</li>" for z in ZONES)
    return f'''<section class="zones container" aria-labelledby="zones-title">
  <div class="zones__head">
    <p class="kicker reveal-up">Zone d'intervention</p>
    <h2 id="zones-title" class="split">Morestel et les communes avoisinantes</h2>
    <p class="reveal-up">Location de bennes dans un rayon de 30 km autour de Morestel, débarras jusqu'à 50 km, en Isère (38), dans l'Ain (01) et en Savoie (73). Quelques communes où nous intervenons :</p>
  </div>
  <ul class="zones__list reveal-stagger">{lis}</ul>
</section>'''


def contact_html(root, heading_tag="h2", heading="Contactez LG Service pour un débarras ou des bennes à Morestel"):
    t = (SRC / "partials" / "contact.html").read_text()
    return (t.replace("{{heading_tag}}", heading_tag).replace("{{heading}}", heading)
             .replace("{{root}}", root))


def render_tokens(body, root, page):
    def img_sub(m):
        parts = [p.strip() for p in m.group(1).split("|")]
        name, alt = parts[0], parts[1]
        cls = parts[2] if len(parts) > 2 else ""
        eager = len(parts) > 3 and parts[3] == "eager"
        return img_tag(root, name, alt, cls, eager)

    body = re.sub(r"\[\[img (.+?)\]\]", img_sub, body)
    body = re.sub(r"\[\[faq (\w+)\]\]", lambda m: faq_html(m.group(1)), body)
    body = body.replace("[[zones]]", zones_html())
    body = re.sub(r"\[\[contact( h1)?\]\]",
                  lambda m: contact_html(root, "h1" if m.group(1) else "h2",
                                         "Contactez la société LG Service pour demander un débarras ou des bennes à Morestel" if m.group(1)
                                         else "Contactez LG Service pour un débarras ou des bennes à Morestel"), body)
    body = body.replace("[[cta]]", (SRC / "partials" / "cta.html").read_text())
    body = body.replace("[[arrow]]", ARROW)
    if page.get("crumb"):
        body = body.replace("[[breadcrumb]]",
                            f'<nav class="breadcrumb" aria-label="Fil d\'Ariane"><a href="{root or "./"}">Accueil</a><span aria-hidden="true">/</span><span aria-current="page">{esc(page["crumb"])}</span></nav>')
    return body.replace("{{root}}", root)


def jsonld(page):
    url = f"{SITE}/{page['path']}"
    biz_id = f"{SITE}/#entreprise"
    graph = [{
        "@type": "LocalBusiness",
        "@id": biz_id,
        "name": BUSINESS["name"],
        "legalName": "LG SERVICE",
        "description": "Débarras, location de bennes de 3 à 12 m³, achat et vente de métaux à Morestel et alentours, pour particuliers et professionnels.",
        "url": f"{SITE}/",
        "logo": f"{SITE}/assets/img/logo.png",
        "image": [f"{SITE}/assets/img/og-image.jpg", f"{SITE}/assets/img/camion-benne-lg-service.webp"],
        "telephone": BUSINESS["phone"],
        "email": BUSINESS["email"],
        "foundingDate": "2021",
        "vatID": "FR87901394544",
        "taxID": "90139454400018",
        "address": {"@type": "PostalAddress", "streetAddress": BUSINESS["street"], "postalCode": BUSINESS["postal"],
                    "addressLocality": BUSINESS["city"], "addressRegion": "Auvergne-Rhône-Alpes", "addressCountry": "FR"},
        "areaServed": [{"@type": "City", "name": z} for z in ZONES],
        "openingHoursSpecification": [{"@type": "OpeningHoursSpecification",
                                       "dayOfWeek": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                                       "opens": "00:00", "closes": "23:59"}],
        "paymentAccepted": "Chèque, Espèces, Virement",
        "currenciesAccepted": "EUR",
        "sameAs": [BUSINESS["facebook"]],
        "hasOfferCatalog": {"@type": "OfferCatalog", "name": "Services LG Service", "itemListElement": [
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Location de bennes", "url": f"{SITE}/location-bennes/"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Débarras", "url": f"{SITE}/debarras/"}},
            {"@type": "Offer", "itemOffered": {"@type": "Service", "name": "Achat et vente de métaux", "url": f"{SITE}/vente-metaux/"}},
        ]},
    }, {
        "@type": "WebSite", "@id": f"{SITE}/#site", "url": f"{SITE}/", "name": "LG Service",
        "inLanguage": "fr-FR", "publisher": {"@id": biz_id},
    }, {
        "@type": "WebPage", "@id": url, "url": url, "name": page["title"], "description": page["desc"],
        "inLanguage": "fr-FR", "isPartOf": {"@id": f"{SITE}/#site"}, "about": {"@id": biz_id},
    }]
    if page.get("crumb"):
        graph.append({"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Accueil", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": page["crumb"], "item": url},
        ]})
    if page.get("service"):
        name, desc = page["service"]
        graph.append({"@type": "Service", "name": name, "serviceType": name, "description": desc, "url": url,
                      "provider": {"@id": biz_id},
                      "areaServed": {"@type": "GeoCircle", "geoMidpoint": {"@type": "Place", "name": "Morestel"},
                                     "geoRadius": "50000" if page["src"] == "debarras" else "30000"}})
    if page.get("faq"):
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in FAQ[page["faq"]]]})
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=1)


def build_page(page):
    depth = 0 if page.get("flat") or page["out"] == "index.html" else page["out"].count("/")
    root = "../" * depth
    url = f"{SITE}/{page['path']}"
    body = render_tokens((SRC / "pages" / f"{page['src']}.html").read_text(), root, page)
    image = f"{SITE}/assets/img/og-image.jpg"
    robots = "noindex, follow" if page.get("noindex") else "index, follow, max-image-preview:large"
    home = root or "./"

    nav = "\n".join(
        f'      <a href="{root}{href}"{" aria-current=\"page\" class=\"is-active\"" if href == page["path"] else ""}>{label}</a>'
        for href, label in NAV)
    menu = "\n".join(f'      <a href="{root}{href}"><i>0{i + 2}</i>{label}</a>' for i, (href, label) in enumerate(NAV))
    zones_footer = ", ".join(ZONES[:8])
    loader = ""
    if page.get("loader"):
        loader = f'''  <div class="loader" aria-hidden="true">
    <div class="loader__inner">
      <img src="{root}assets/img/logo.png" alt="" class="loader__logo" width="96" height="96">
      <div class="loader__bar"><span></span></div>
    </div>
    <div class="loader__panel loader__panel--1"></div>
    <div class="loader__panel loader__panel--2"></div>
  </div>
'''
    canonical = "" if page.get("noindex") else f'  <link rel="canonical" href="{url}">\n'

    return f'''<!doctype html>
<html lang="fr">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(page["title"])}</title>
  <meta name="description" content="{esc(page["desc"])}">
  <meta name="robots" content="{robots}">
{canonical}  <meta name="theme-color" content="#0e0e10">
  <meta name="geo.region" content="FR-38">
  <meta name="geo.placename" content="Morestel">
  <meta property="og:locale" content="fr_FR">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="LG Service">
  <meta property="og:title" content="{esc(page["title"])}">
  <meta property="og:description" content="{esc(page["desc"])}">
  <meta property="og:url" content="{url}">
  <meta property="og:image" content="{image}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Camion LG Service chargeant une benne à Morestel">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="icon" type="image/png" href="{root}assets/img/favicon.png">
  <link rel="apple-touch-icon" href="{root}assets/img/apple-touch-icon.png">
  <link rel="manifest" href="{root}site.webmanifest">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{root}assets/css/style.css">
  <script>document.documentElement.classList.add('js');</script>
  <script type="application/ld+json">
{jsonld(page)}
  </script>
</head>
<body>
  <a class="skip" href="#contenu">Aller au contenu</a>
{loader}  <div class="cursor" aria-hidden="true"><span class="cursor__dot"></span><span class="cursor__ring"></span></div>
  <div class="progress" aria-hidden="true"></div>

  <header class="header">
    <a href="{home}" class="brand" aria-label="LG Service – accueil">
      <span class="brand__logo"><img src="{root}assets/img/logo.png" alt="Logo LG Service" width="40" height="40"></span>
      <span class="brand__name">LG <b>Service</b></span>
    </a>
    <nav class="nav" aria-label="Navigation principale">
{nav}
    </nav>
    <a href="tel:{BUSINESS["phone"]}" class="btn btn--sm btn--yellow header__cta magnetic" aria-label="Appeler LG Service au {BUSINESS["phone_display"]}">
      {PHONE_ICON}
      <span>{BUSINESS["phone_display"]}</span>
    </a>
    <button class="burger" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="menu"><span></span><span></span></button>
  </header>

  <div class="menu" id="menu" aria-hidden="true">
    <nav class="menu__nav" aria-label="Menu mobile">
      <a href="{home}"><i>01</i>Accueil</a>
{menu}
    </nav>
    <div class="menu__foot">
      <a href="tel:{BUSINESS["phone"]}">{BUSINESS["phone_display"]}</a>
      <a href="mailto:{BUSINESS["email"]}">{BUSINESS["email"]}</a>
    </div>
  </div>

  <main id="contenu">
{body}
  </main>

  <footer class="footer">
    <div class="container footer__top">
      <div class="footer__brand">
        <span class="brand__logo brand__logo--lg"><img src="{root}assets/img/logo.png" alt="LG Service" width="72" height="72" loading="lazy"></span>
        <p>Débarras, location de bennes, achat et vente de métaux à Morestel : nous écoutons vos besoins et vous proposons des solutions adaptées, pour les particuliers et les professionnels.</p>
      </div>
      <div class="footer__col">
        <p class="footer__h">Nos services</p>
        <a href="{root}location-bennes/">Location de bennes à Morestel</a>
        <a href="{root}debarras/">Débarras de maison et locaux</a>
        <a href="{root}vente-metaux/">Achat et vente de métaux</a>
        <a href="{root}a-propos/">À propos</a>
        <a href="{root}contact/">Contact et devis</a>
      </div>
      <div class="footer__col">
        <p class="footer__h">Informations pratiques</p>
        <a href="mailto:{BUSINESS["email"]}">Écrivez-nous</a>
        <a href="tel:{BUSINESS["phone"]}">Appelez-nous : {BUSINESS["phone_display"]}</a>
        <span>{BUSINESS["street"]}, {BUSINESS["postal"]} {BUSINESS["city"]}</span>
        <span>Ouvert 24h/24, 7j/7</span>
        <span class="footer__zones">Intervention : {esc(zones_footer)}…</span>
      </div>
    </div>
    <div class="footer__giant" aria-hidden="true">LG SERVICE</div>
    <div class="container footer__bottom">
      <span>© <span id="year">{date.today().year}</span> LG Service</span>
      <span class="footer__legal"><a href="{root}mentions-legales/">Mentions légales</a> · <a href="{root}vie-privee/">Vie privée</a></span>
      <a href="#contenu" class="totop">Haut de page ↑</a>
    </div>
  </footer>

  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
  <script defer src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
  <script defer src="https://cdn.jsdelivr.net/npm/lenis@1.1.13/dist/lenis.min.js"></script>
  <script defer src="{root}assets/js/main.js"></script>
</body>
</html>
'''


def main():
    today = date.today().isoformat()
    urls = []
    for page in PAGES:
        out = ROOT / page["out"]
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(build_page(page))
        if not page.get("noindex"):
            urls.append(f"  <url><loc>{SITE}/{page['path']}</loc><lastmod>{today}</lastmod><priority>{page['priority']}</priority></url>")
        print("écrit", page["out"])
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + "\n".join(urls) + "\n</urlset>\n")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nDisallow: /src/\n\nSitemap: {SITE}/sitemap.xml\n")
    print("écrit sitemap.xml, robots.txt")


if __name__ == "__main__":
    main()
