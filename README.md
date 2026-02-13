# DISPARUS.ORG

![Status](https://img.shields.io/badge/status-active-success.svg)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.1.2-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

> **Plateforme collaborative open-source dédiée au signalement, à la recherche et à la géolocalisation de personnes et d'animaux disparus.**

DISPARUS.ORG est une solution complète permettant de centraliser les avis de recherche, de générer instantanément des affiches d'alerte multilingues et de coordonner les efforts de la communauté via une carte interactive et des outils de modération avancés.

---

## 📚 Documentation Complète

L'ensemble de la documentation technique, fonctionnelle et commerciale est disponible dans le dossier [`docs/`](./docs/) :

### Technique & Développement
*   📖 **[Bible des Fonctionnalités](./docs/disparus_org_features_full_list.md)** : Inventaire exhaustif de chaque feature (validation, logique métier, UX).
*   🏗️ **[Architecture Technique](./docs/disparus_org_architecture_technique.md)** : Stack, schéma de base de données, flux de données.
*   🔌 **[API Reference](./docs/disparus_org_api_reference.md)** : Documentation des endpoints JSON.
*   🚀 **[Guide de Déploiement](./docs/disparus_org_guide_deploiment.md)** : Installation, configuration, mise en production.

### Guides Utilisateurs
*   👥 **[Guide Utilisateur](./docs/disparus_org_guide_utilisateur.md)** : Manuel pour le grand public (signalement, recherche).
*   🛡️ **[Guide Administrateur](./docs/disparus_org_guide_administrateur.md)** : Manuel pour le back-office (modération, settings).

### Vision & Business
*   🎯 **[Vision Produit](./docs/disparus_org_vision_produit.md)** : Objectifs à long terme et philosophie.
*   🤝 **[Offre Partenariats](./docs/disparus_org_offre_partenariats.md)** : Collaboration avec ONG et institutions.

---

## ✨ Fonctionnalités Clés

*   **Signalement Simplifié :** Formulaire intuitif pour Personnes et Animaux avec géolocalisation automatique.
*   **Génération de Documents (IA) :**
    *   **Affiches PDF A4 :** QR Code dynamique, mise en page bilingue (FR/EN).
    *   **Images Réseaux Sociaux :** Format carré optimisé avec bandeau de statut (Rouge/Vert/Gris) et date incrustée.
*   **Carte Interactive :** Visualisation globale avec clustering pour les zones denses.
*   **Moteur de Recherche :** Rapide et tolérant aux fautes (FTS5 SQLite).
*   **Système de Contributions :** Témoignages, observations et changements de statut validés par modération.
*   **Modération Automatisée :** Détection de nudité et violence sur les photos via API externe (APILayer).
*   **Administration RBAC :** Gestion fine des rôles (Admin, Modérateur, ONG, Secours).
*   **Sécurité :** Rate Limiting par IP, Protection CSRF, Hachage Argon2.

---

## 🛠️ Stack Technique

*   **Backend :** Python 3.10+, Flask (Blueprints), Gunicorn.
*   **Base de Données :** SQLAlchemy (SQLite / PostgreSQL), FTS5 Search.
*   **Frontend :** Jinja2 Templates, Tailwind CSS, Leaflet.js.
*   **Traitements Async :** `aiohttp` (API externes), `Pillow` (Images), `ReportLab` (PDF).

---

## 🚀 Démarrage Rapide (Dev)

```bash
# 1. Cloner le projet
git clone https://github.com/votre-orga/disparus-org.git
cd disparus-org

# 2. Créer l'environnement virtuel
python3 -m venv venv
source venv/bin/activate

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Initialiser la base de données
python init_db.py

# 5. Lancer le serveur de développement
python main.py
```
> L'application sera accessible sur `http://localhost:5000`.
> Compte Admin par défaut : `admin` / `(Voir logs ou console)`

---

## 📂 Architecture

```
/
├── models/             # Définitions de la BDD (Disparu, User, Contribution)
├── routes/             # Contrôleurs (Public, Admin, API)
├── services/           # Logique métier (Modération, Upload)
├── utils/              # Générateurs (PDF, Images, i18n)
├── templates/          # Vues HTML Jinja2
└── static/             # Assets (CSS, JS, Images)
```

---

## 🤝 Contribuer

Les contributions sont les bienvenues ! Merci de consulter le [Guide de Déploiement](./docs/disparus_org_guide_deploiment.md) pour configurer votre environnement de développement.

---
*Fait avec ❤️ pour aider à retrouver ceux qui comptent.*
