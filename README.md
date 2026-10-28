# LG Service — site web

Site vitrine de LG Service (débarras, location de bennes, achat et vente de métaux à Morestel).

## Structure

| Adresse | Fichier source |
|---|---|
| `/` | `src/pages/accueil.html` |
| `/location-bennes/` | `src/pages/location-bennes.html` |
| `/debarras/` | `src/pages/debarras.html` |
| `/vente-metaux/` | `src/pages/vente-metaux.html` |
| `/a-propos/` | `src/pages/a-propos.html` |
| `/contact/` | `src/pages/contact.html` |
| `/mentions-legales/`, `/vie-privee/`, `404.html` | `src/pages/…` |

Les adresses reprennent celles de l'ancien site pour conserver le référencement.

## Modifier le site

1. Modifier le contenu dans `src/pages/` (ou `src/partials/` pour le contact et le bandeau d'appel).
   Titres, descriptions Google, FAQ et communes desservies sont dans `build.py`.
2. Régénérer les pages : `python3 build.py`
3. Commiter les fichiers générés et pousser sur `main` (déploiement GitHub Pages automatique).

`build.py` produit aussi `sitemap.xml` et `robots.txt`. La constante `SITE` définit l'adresse
officielle utilisée pour les balises canonical, Open Graph et le sitemap.

## SEO intégré

- Title et meta description uniques par page, canonical, Open Graph / Twitter
- Données structurées JSON-LD : LocalBusiness, Service, FAQPage, BreadcrumbList, WebSite
- Sitemap, robots.txt, page 404, fil d'Ariane, maillage interne entre services
- Images WebP nommées par mots-clés, avec `alt`, dimensions et versions mobiles (`srcset`)
