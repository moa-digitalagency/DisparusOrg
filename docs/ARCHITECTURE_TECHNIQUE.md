# Architecture Technique

Ce document décrit l'architecture technique de la plateforme DISPARUS.ORG.

## 1. Stack Technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Python Flask | 3.10+ |
| Base de données | PostgreSQL | 14+ |
| ORM | SQLAlchemy | 2.x |
| Frontend | HTML/Jinja2 + Tailwind CSS | CDN |
| Cartographie | Leaflet + OpenStreetMap | 1.9 |
| Internationalisation | Flask-Babel | - |
| Génération PDF | ReportLab | - |
| QR Codes | qrcode + Pillow | - |
| Images | Pillow (PIL) | - |

## 2. Structure du Projet

```text
disparus.org/
├── app.py                 # Configuration Flask et initialisation
├── config.py              # Classes de configuration
├── main.py                # Point d'entrée de l'application
├── init_db.py             # Initialisation base + migrations
├── init_db_demo.py        # Données de démonstration
│
├── routes/                # Blueprints Flask
│   ├── __init__.py        # Enregistrement des blueprints
│   ├── public.py          # Routes publiques (/, /recherche, /signaler, /disparu)
│   ├── admin.py           # Routes administration (/admin/*)
│   └── api.py             # API JSON (/api/*)
│
├── models/                # Modèles SQLAlchemy
│   ├── __init__.py        # Export des modèles + instance db
│   ├── disparu.py         # Personne disparue
│   ├── contribution.py    # Contributions/témoignages
│   ├── user.py            # Utilisateurs et rôles
│   ├── activity_log.py    # Journal d'activité
│   ├── download.py        # Suivi des téléchargements
│   └── settings.py        # Paramètres du site
│
├── templates/             # Templates Jinja2
│   ├── base.html          # Template de base avec SEO
│   ├── index.html         # Page d'accueil
│   ├── ...
│
├── statics/               # Fichiers statiques
│   ├── css/               # Feuilles de style
│   ├── js/                # JavaScript
│   ├── img/               # Images, icônes
│   └── uploads/           # Photos uploadées
│
├── utils/                 # Fonctions utilitaires (Geo, PDF, Search)
├── services/              # Logique métier (Signalement, Analytics)
├── security/              # Sécurité (Auth, Rate Limit)
└── docs/                  # Documentation
```

## 3. Schéma de Base de Données

### Table `disparus_flask`
Stocke les informations sur les personnes disparues.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire auto-incrémentée |
| public_id | VARCHAR(6) | Identifiant public unique (ex: ABC123) |
| person_type | VARCHAR(20) | Type: child, adult, elderly, animal, teenager |
| first_name | VARCHAR(100) | Prénom |
| last_name | VARCHAR(100) | Nom |
| age | INTEGER | Âge au moment de la disparition |
| sex | VARCHAR(20) | Sexe |
| country | VARCHAR(100) | Pays de disparition |
| city | VARCHAR(100) | Ville de disparition |
| physical_description | TEXT | Description physique |
| photo_url | VARCHAR(500) | Chemin vers la photo |
| disappearance_date | DATETIME | Date et heure de disparition |
| circumstances | TEXT | Circonstances de la disparition |
| latitude | FLOAT | Coordonnée GPS latitude |
| longitude | FLOAT | Coordonnée GPS longitude |
| clothing | TEXT | Description des vêtements |
| objects | TEXT | Objets portés |
| contacts | JSON | Liste des contacts (nom, téléphone, email, lien) |
| status | VARCHAR(20) | Statut: missing, found, deceased |
| is_flagged | BOOLEAN | Contenu signalé pour modération |
| view_count | INTEGER | Nombre de vues |
| created_at | DATETIME | Date de création |
| updated_at | DATETIME | Date de modification |

### Table `contributions_flask`
Stocke les contributions des citoyens.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| disparu_id | INTEGER | FK vers disparus_flask |
| contribution_type | VARCHAR(50) | Type: seen, info, police, found, other |
| details | TEXT | Détails de la contribution |
| latitude | FLOAT | Coordonnée GPS du lieu |
| longitude | FLOAT | Coordonnée GPS |
| location_name | VARCHAR(200) | Nom du lieu |
| observation_date | DATETIME | Date de l'observation |
| proof_url | VARCHAR(500) | Photo ou preuve |
| person_state | VARCHAR(50) | État de la personne |
| is_verified | BOOLEAN | Contribution vérifiée |
| is_approved | BOOLEAN | Contribution approuvée |
| approved_by | VARCHAR(100) | Modérateur ayant approuvé |
| created_at | DATETIME | Date de création |

### Table `users_flask`
Gestion des comptes utilisateurs.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| email | VARCHAR(255) | Email unique |
| username | VARCHAR(100) | Nom d'utilisateur |
| password_hash | VARCHAR(255) | Hash du mot de passe |
| role | VARCHAR(20) | Rôle (admin, moderator, ngo, secours, user) |
| is_active | BOOLEAN | Compte actif |
| last_login | DATETIME | Dernière connexion |
| created_at | DATETIME | Date de création |

### Table `moderation_reports_flask`
Signalements de contenu inapproprié.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| target_type | VARCHAR(50) | Type de cible (disparu, contribution) |
| target_id | INTEGER | ID de la cible |
| reason | VARCHAR(50) | Raison |
| details | TEXT | Détails |
| status | VARCHAR(20) | Statut: pending, resolved |
| created_at | DATETIME | Date de création |

### Table `activity_logs_flask`
Journal d'activité de la plateforme (Audit Trail).

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| username | VARCHAR(100) | Nom d'utilisateur ou "visiteur" |
| action | VARCHAR(100) | Description de l'action |
| action_type | VARCHAR(50) | Type: auth, view, create, update, delete |
| ip_address | VARCHAR(50) | Adresse IP |
| severity | VARCHAR(20) | Sévérité: info, warning, error, critical |
| is_security_event | BOOLEAN | Événement de sécurité |
| created_at | DATETIME | Date de création |

### Table `downloads_flask`
Suivi des téléchargements.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Clé primaire |
| disparu_public_id | VARCHAR(10) | ID public |
| file_type | VARCHAR(20) | Type: pdf, png, jpg |
| download_type | VARCHAR(50) | Type: pdf_fiche, image_social... |
| created_at | DATETIME | Date |

### Table `site_settings_flask`
Configuration dynamique du site.

| Colonne | Type | Description |
|---------|------|-------------|
| key | VARCHAR(100) | Clé unique du paramètre |
| value | TEXT | Valeur |
| category | VARCHAR(50) | Catégorie (seo, security...) |

## 4. Flux de Données

### Signalement d'une disparition
1.  **Utilisateur** remplit le formulaire (`/signaler`).
2.  **Backend** valide les données et l'image (MIME check).
3.  **Service** crée l'entrée `Disparu` et génère un `public_id` unique.
4.  **Redirection** vers la fiche créée.

### Contribution citoyenne
1.  **Visiteur** sur une fiche, clique "Contribuer".
2.  **Formulaire** (Observation, Info, Trouvé).
3.  **Contribution** créée avec statut `is_approved=False` (si modération active).
4.  Si type="found", notification aux admins pour changement de statut.

## 5. Sécurité

*   **Authentification Admin** : Basée sur `ADMIN_USERNAME`/`ADMIN_PASSWORD` (Env vars) + Session sécurisée.
*   **CSRF** : Protection globale via Flask-WTF.
*   **Rate Limiting** : Limite les abus sur l'API et les formulaires (module `security/rate_limit.py`).
*   **Uploads** : Fichiers renommés (`secure_filename`), extensions limitées.

## 6. SEO et Référencement

*   **Sitemap** : Généré dynamiquement sur `/sitemap.xml`.
*   **Open Graph** : Balises `og:image`, `og:title` dynamiques pour le partage social.
*   **Robots.txt** : Configuration dynamique autorisant les bots IA.

## 7. Performance

*   **Lazy Loading** : Images chargées à la demande.
*   **Indexation** : Index SQL sur `public_id` et `status`.
*   **Stateless** : Application conçue pour être scalable horizontalement (hors uploads locaux).
