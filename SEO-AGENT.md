# Consignes de l'agent de référencement LG Service

Ce fichier est lu par l'agent IA à chaque passage. Modifiez-le pour changer son comportement.

## Contexte
- Site vitrine de LG Service : débarras, location de bennes (3 à 12 m³), achat et vente de métaux,
  à Morestel et alentours (bennes : 30 km, débarras : 50 km). Entreprise familiale fondée en 2021.
- Site statique généré par `build.py` à partir de `src/pages/` et `src/partials/`.
  Ne jamais modifier les fichiers générés à la main (`index.html`, `*/index.html`, `404.html`,
  `sitemap.xml`, `robots.txt`) : modifier les sources puis lancer `python3 build.py`.
- Publication : un push sur `main` déclenche le déploiement GitHub Pages
  (https://k6vft5k7cw-glitch.github.io/lg-service-/).
- Adresse officielle (canonical) : constante `SITE` dans `build.py`. Ne pas la changer.

## Faits autorisés (ne jamais en inventer d'autres)
- Téléphone 06 81 21 93 60 · contact@debarras-lg-service.fr · Chemin De La Plaine, 01300 Brégnier-Cordon
- Ouvert 24h/24, 7j/7 · Paiement : chèques, espèces, virements
- Bennes de 3 à 12 m³ pour déchets industriels, bois, gravats, ferrailles ; livrées et reprises par camion ;
  livraison possible dans la journée sous réserve de disponibilité ; tarification au tonnage
- Débarras de granges, garages, ateliers, maisons, caves, locaux d'entreprise (succession, vente, déménagement) ;
  évaluation du volume, mise en place de bennes, tri, évacuation vers centres de tri et de valorisation
- Rachat et revente de cuivre, laiton, fils électriques PVC, ferraille, batteries
- SIRET 90139454400018 · TVA FR87901394544

## Interdits
- Inventer des prix, tarifs, délais chiffrés, garanties, certifications, labels, avis clients,
  témoignages, chiffres (nombre de clients, tonnages…), noms de clients ou partenaires.
- Promettre des services non listés ci-dessus (ex. : amiante, déchets dangereux, vidage de fosses…).
- Modifier les mentions légales, les coordonnées, le domaine, ajouter un fichier `CNAME`.
- Supprimer des pages existantes ou changer leurs adresses.
- Bourrage de mots-clés, pages satellites par ville quasi identiques, texte caché, contenu copié d'autres sites.
- Plus d'un nouvel article par semaine.

## Qualité avant chaque push (obligatoire)
1. `python3 build.py` sans erreur.
2. Servir le site (`python3 -m http.server`) et vérifier avec Playwright (préinstallé, `require('playwright')`)
   que chaque page du sitemap répond 200, sans erreur JavaScript, sans débordement horizontal à 390 px,
   avec un seul `<h1>`, et que le JSON-LD se parse.
3. Titles ≤ 60 caractères, meta descriptions ≤ 160, uniques par page.
4. En cas de doute ou d'échec : ne rien pousser, l'écrire dans le journal.

## Journal
Ajouter à chaque passage une entrée datée en tête de `SEO-LOG.md` : vérifications faites,
problèmes trouvés, modifications publiées (avec le commit), idées pour la suite.
