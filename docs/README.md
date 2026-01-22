# DISPARUS.ORG - Documentation

Documentation de la plateforme DISPARUS.ORG pour la recherche des personnes disparues en Afrique.

## Sommaire

### Documentation technique
- [Architecture technique](./ARCHITECTURE.md) - Structure du code, base de donnees, flux de donnees
- [Fonctionnalites detaillees](./FONCTIONNALITES.md) - Description de chaque fonctionnalite
- [Installation et deploiement](./INSTALLATION.md) - Guide d'installation, configuration serveur
- [API Reference](./API.md) - Documentation des endpoints API REST

### Documentation fonctionnelle
- [Guide utilisateur](./GUIDE_UTILISATEUR.md) - Signaler, rechercher, contribuer
- [Guide administrateur](./GUIDE_ADMIN.md) - Gestion, moderation, configuration

### Documentation commerciale
- [Presentation du projet](./PRESENTATION.md) - Vision, mission, impact social
- [Partenariats](./PARTENARIATS.md) - Opportunites de collaboration

---

## A propos de DISPARUS.ORG

DISPARUS.ORG est une plateforme humanitaire citoyenne dediee a la recherche des personnes disparues sur le continent africain. Elle couvre 54 pays et plus de 650 villes, offrant un outil gratuit et accessible pour signaler une disparition ou contribuer a des recherches en cours.

### Fonctionnalites principales

**Pour les familles et citoyens :**
- Signalement rapide avec photo, localisation GPS et description
- Recherche par nom, ville, pays ou identifiant unique
- Contribution aux recherches (temoignages, observations)
- Telechargement de fiches PDF, images reseaux sociaux, QR codes
- Partage direct sur 12 plateformes (WhatsApp, Facebook, X, Telegram...)
- Compteur de temps depuis la disparition
- Carte interactive avec localisation des disparitions

**Pour les organisations :**
- Interface multilingue (francais/anglais)
- Mode hors-ligne (PWA)
- API REST pour integration
- SEO optimise avec sitemap dynamique
- Export des donnees (JSON, CSV)

**Pour les administrateurs :**
- Tableau de bord avec statistiques
- Moderation des contenus et contributions
- Gestion des utilisateurs et roles
- Journalisation des activites
- Sauvegarde et restauration des donnees
- Configuration SEO et parametres du site

### Couverture geographique

54 pays africains couverts :
- Afrique du Nord : Algerie, Egypte, Libye, Maroc, Mauritanie, Tunisie
- Afrique de l'Ouest : Benin, Burkina Faso, Cote d'Ivoire, Gambie, Ghana, Guinee, Guinee-Bissau, Liberia, Mali, Niger, Nigeria, Senegal, Sierra Leone, Togo
- Afrique Centrale : Cameroun, Centrafrique, Congo, Gabon, Guinee equatoriale, RD Congo, Tchad
- Afrique de l'Est : Burundi, Comores, Djibouti, Erythree, Ethiopie, Kenya, Madagascar, Maurice, Ouganda, Rwanda, Seychelles, Somalie, Soudan, Soudan du Sud, Tanzanie
- Afrique Australe : Afrique du Sud, Angola, Botswana, Eswatini, Lesotho, Malawi, Mozambique, Namibie, Zambie, Zimbabwe

### Chiffres cles

- 650+ villes referencees
- 3 statuts de suivi : Porte(e) Disparu(e), Retrouve(e), Decede(e)
- Support bilingue FR/EN
- Compatible mobile, tablette, desktop

---

## Demarrage rapide

### Prerequis
- Python 3.11+
- PostgreSQL 14+
- Variables d'environnement configurees

### Installation
```bash
pip install -r requirements.txt
python init_db.py
python main.py
```

### Acces
- Site public : http://localhost:5000
- Administration : http://localhost:5000/admin/login

---

## Licence et credits

Plateforme developpee dans un but humanitaire. 
Contact : voir les parametres du site dans l'administration.
