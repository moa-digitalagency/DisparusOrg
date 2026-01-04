# Architecture technique

Ce document decrit l'architecture technique de la plateforme DISPARUS.ORG.

## Stack technologique

| Composant | Technologie | Version |
|-----------|-------------|---------|
| Backend | Python Flask | 3.x |
| Base de donnees | PostgreSQL | 14+ |
| ORM | SQLAlchemy | 2.x |
| Frontend | HTML/Jinja2 + Tailwind CSS | - |
| Cartographie | Leaflet + OpenStreetMap | 1.9 |
| Internationalisation | Flask-Babel | - |
| Generation PDF | ReportLab | - |
| QR Codes | qrcode + Pillow | - |

## Structure des dossiers

```
disparus.org/
├── app.py                 # Configuration Flask et initialisation
├── config.py              # Classes de configuration
├── main.py                # Point d'entree de l'application
├── init_db.py             # Script d'initialisation de la base
│
├── routes/                # Blueprints Flask
│   ├── __init__.py        # Enregistrement des blueprints
│   ├── public.py          # Routes publiques (/, /recherche, /signaler, /disparu)
│   ├── admin.py           # Routes administration (/admin/*)
│   └── api.py             # API JSON (/api/*)
│
├── models/                # Modeles SQLAlchemy
│   ├── __init__.py        # Export des modeles
│   ├── disparu.py         # Personne disparue
│   ├── contribution.py    # Contributions/temoignages
│   ├── user.py            # Utilisateurs et roles
│   ├── activity_log.py    # Journal d'activite
│   ├── download.py        # Suivi des telechargements
│   └── settings.py        # Parametres du site
│
├── templates/             # Templates Jinja2
│   ├── base.html          # Template de base
│   ├── index.html         # Page d'accueil
│   ├── search.html        # Page de recherche
│   ├── report.html        # Formulaire de signalement
│   ├── detail.html        # Fiche personne disparue
│   ├── admin_*.html       # Pages administration
│   └── moderation.html    # Page moderation
│
├── statics/               # Fichiers statiques
│   ├── css/               # Feuilles de style
│   ├── js/                # JavaScript (dont sw.js)
│   ├── img/               # Images et icones
│   └── uploads/           # Fichiers uploades
│
├── utils/                 # Fonctions utilitaires
│   ├── geo.py             # Donnees geographiques (pays/villes)
│   ├── pdf_gen.py         # Generation PDF et images
│   └── search.py          # Indexation recherche
│
├── services/              # Logique metier
│   ├── signalement.py     # Gestion des signalements
│   ├── notifications.py   # Notifications email/SMS
│   └── analytics.py       # Statistiques plateforme
│
├── security/              # Securite
│   ├── auth.py            # Decorateurs d'authentification
│   └── rate_limit.py      # Limitation de requetes
│
├── algorithms/            # Algorithmes d'analyse
│   ├── clustering.py      # Zones de concentration
│   └── matching.py        # Correspondance photos
│
├── lang/                  # Traductions
│   ├── fr.json            # Francais
│   └── en.json            # Anglais
│
└── docs/                  # Documentation
```

## Schema de base de donnees

### Table `disparus_flask`

Stocke les informations sur les personnes disparues.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Cle primaire auto-incrementee |
| public_id | VARCHAR(6) | Identifiant public unique (ex: ABC123) |
| person_type | VARCHAR(20) | Type: enfant, adulte, personne_agee |
| first_name | VARCHAR(100) | Prenom |
| last_name | VARCHAR(100) | Nom |
| age | INTEGER | Age au moment de la disparition |
| sex | VARCHAR(20) | Sexe |
| country | VARCHAR(100) | Pays de disparition |
| city | VARCHAR(100) | Ville de disparition |
| physical_description | TEXT | Description physique |
| photo_url | VARCHAR(500) | Chemin vers la photo |
| disappearance_date | DATETIME | Date et heure de disparition |
| circumstances | TEXT | Circonstances de la disparition |
| latitude | FLOAT | Coordonnee GPS latitude |
| longitude | FLOAT | Coordonnee GPS longitude |
| clothing | TEXT | Description des vetements |
| objects | TEXT | Objets portes |
| contacts | JSON | Liste des contacts (nom, telephone, email, lien) |
| status | VARCHAR(20) | Statut: missing, found, deceased |
| is_flagged | BOOLEAN | Contenu signale pour moderation |
| view_count | INTEGER | Nombre de vues |
| created_at | DATETIME | Date de creation |
| updated_at | DATETIME | Date de modification |

### Table `contributions_flask`

Stocke les contributions des citoyens (temoignages, observations).

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Cle primaire |
| disparu_id | INTEGER | FK vers disparus_flask |
| contribution_type | VARCHAR(50) | Type: sighting, information, found, other |
| details | TEXT | Details de la contribution |
| latitude | FLOAT | Coordonnee GPS du lieu d'observation |
| longitude | FLOAT | Coordonnee GPS |
| location_name | VARCHAR(200) | Nom du lieu |
| observation_date | DATETIME | Date de l'observation |
| proof_url | VARCHAR(500) | Photo ou preuve |
| person_state | VARCHAR(50) | Etat de la personne observee |
| return_circumstances | TEXT | Circonstances du retour (si retrouve) |
| contact_name | VARCHAR(100) | Nom du contributeur |
| contact_phone | VARCHAR(50) | Telephone |
| contact_email | VARCHAR(100) | Email |
| is_verified | BOOLEAN | Contribution verifiee |
| is_approved | BOOLEAN | Contribution approuvee |
| approved_by | VARCHAR(100) | Moderateur ayant approuve |
| approved_at | DATETIME | Date d'approbation |
| created_at | DATETIME | Date de creation |

### Table `users_flask`

Gestion des comptes utilisateurs.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Cle primaire |
| email | VARCHAR(255) | Email unique |
| username | VARCHAR(100) | Nom d'utilisateur |
| password_hash | VARCHAR(255) | Hash du mot de passe |
| first_name | VARCHAR(100) | Prenom |
| last_name | VARCHAR(100) | Nom |
| phone | VARCHAR(50) | Telephone |
| organization | VARCHAR(200) | Organisation |
| role_id | INTEGER | FK vers roles_flask |
| role | VARCHAR(20) | Role (admin, moderator, ngo, secours, user) |
| is_active | BOOLEAN | Compte actif |
| is_verified | BOOLEAN | Email verifie |
| last_login | DATETIME | Derniere connexion |
| last_login_ip | VARCHAR(50) | IP de derniere connexion |
| login_count | INTEGER | Nombre de connexions |
| created_at | DATETIME | Date de creation |
| updated_at | DATETIME | Date de modification |

### Table `roles_flask`

Definition des roles et permissions.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Cle primaire |
| name | VARCHAR(50) | Nom technique (admin, moderator...) |
| display_name | VARCHAR(100) | Nom affiche |
| description | TEXT | Description du role |
| permissions | JSON | Permissions accordees |
| menu_access | JSON | Menus accessibles |
| is_system | BOOLEAN | Role systeme (non modifiable) |
| created_at | DATETIME | Date de creation |
| updated_at | DATETIME | Date de modification |

### Table `moderation_reports_flask`

Signalements de contenu inapproprie.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Cle primaire |
| target_type | VARCHAR(50) | Type de cible (disparu, contribution) |
| target_id | INTEGER | ID de la cible |
| reason | VARCHAR(50) | Raison (false_info, inappropriate, spam...) |
| details | TEXT | Details du signalement |
| reporter_contact | VARCHAR(200) | Contact du signaleur |
| reporter_ip | VARCHAR(50) | IP du signaleur |
| status | VARCHAR(20) | Statut: pending, resolved |
| reviewed_by | VARCHAR(100) | Moderateur |
| reviewed_at | DATETIME | Date de resolution |
| created_at | DATETIME | Date de creation |

### Table `activity_logs_flask`

Journal d'activite de la plateforme.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Cle primaire |
| user_id | INTEGER | FK vers users_flask (nullable) |
| username | VARCHAR(100) | Nom d'utilisateur ou "visiteur" |
| action | VARCHAR(100) | Description de l'action |
| action_type | VARCHAR(50) | Type: auth, view, create, update, delete, download |
| target_type | VARCHAR(50) | Type de cible |
| target_id | VARCHAR(50) | ID de la cible |
| target_name | VARCHAR(200) | Nom de la cible |
| details | JSON | Details supplementaires |
| ip_address | VARCHAR(50) | Adresse IP |
| user_agent | TEXT | User-Agent du navigateur |
| referrer | TEXT | Page de provenance |
| country | VARCHAR(100) | Pays (geolocalisation IP) |
| city | VARCHAR(100) | Ville |
| is_security_event | BOOLEAN | Evenement de securite |
| severity | VARCHAR(20) | Severite: debug, info, warning, error, critical |
| created_at | DATETIME | Date de creation |

### Table `downloads_flask`

Suivi des telechargements de fichiers.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Cle primaire |
| user_id | INTEGER | FK vers users_flask (nullable) |
| disparu_id | INTEGER | FK vers disparus_flask (nullable) |
| disparu_public_id | VARCHAR(10) | ID public du disparu |
| disparu_name | VARCHAR(200) | Nom du disparu |
| file_type | VARCHAR(20) | Type: pdf, png, jpg, csv, json |
| file_name | VARCHAR(255) | Nom du fichier |
| file_path | VARCHAR(500) | Chemin du fichier |
| file_size | INTEGER | Taille en octets |
| download_type | VARCHAR(50) | Type: pdf_fiche, pdf_qrcode, image_social... |
| ip_address | VARCHAR(50) | Adresse IP |
| user_agent | TEXT | User-Agent |
| country | VARCHAR(100) | Pays |
| city | VARCHAR(100) | Ville |
| created_at | DATETIME | Date de telechargement |

### Table `site_settings_flask`

Configuration du site.

| Colonne | Type | Description |
|---------|------|-------------|
| id | INTEGER | Cle primaire |
| key | VARCHAR(100) | Cle unique du parametre |
| value | TEXT | Valeur |
| value_type | VARCHAR(20) | Type: string, text, boolean, integer, json |
| category | VARCHAR(50) | Categorie: general, seo, security, appearance |
| description | TEXT | Description |
| is_public | BOOLEAN | Accessible publiquement |
| updated_at | DATETIME | Date de modification |
| updated_by | VARCHAR(100) | Auteur de la modification |

## Flux de donnees

### Signalement d'une disparition

```
Utilisateur -> Formulaire (/signaler)
                    |
                    v
            Validation des champs
                    |
                    v
            Upload photo (si presente)
                    |
                    v
            Creation Disparu en base
                    |
                    v
            Generation public_id unique
                    |
                    v
            Redirection vers /disparu/{public_id}
```

### Contribution citoyenne

```
Visiteur -> Fiche personne (/disparu/{id})
                    |
                    v
            Formulaire de contribution
                    |
                    v
            Creation Contribution en base
                    |
                    v
            Si type = "found" -> Mise a jour statut Disparu
                    |
                    v
            Affichage sur la fiche
```

### Moderation

```
Signalement contenu -> ModerationReport cree
                            |
                            v
                    Disparu.is_flagged = True
                            |
                            v
                    Visible dans /admin/moderation
                            |
                            v
            Moderateur resout (conserver/supprimer)
                            |
                            v
                    ActivityLog enregistre
```

## Securite

### Authentification admin

L'acces a l'administration utilise exclusivement les variables d'environnement :
- `ADMIN_USERNAME` : Identifiant administrateur
- `ADMIN_PASSWORD` : Mot de passe administrateur

La session est geree via Flask session avec `SESSION_SECRET`.

### Protection CSRF

Les formulaires incluent une protection CSRF via Flask-WTF.

### Rate Limiting

L'API est protegee par un systeme de limitation de requetes :
- Configurable via `rate_limit_per_minute` dans les parametres
- Decorator `@rate_limit()` sur les endpoints API

### Validation des uploads

- Extensions autorisees : png, jpg, jpeg, gif, webp
- Types MIME verifies
- Noms de fichiers securises via `secure_filename`

## Performance

### Optimisations base de donnees

- Index sur `public_id` pour recherche rapide
- Pool de connexions avec recyclage (300s)
- Pre-ping pour verifier les connexions

### Mise en cache

- Headers `Cache-Control: no-cache` pour eviter les problemes de cache
- Service Worker pour le mode offline (PWA)

### Generation de fichiers

- PDFs generes a la demande (non stockes)
- Images sociales generees a la demande
- QR codes generes dynamiquement
