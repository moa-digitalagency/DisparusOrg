# DISPARUS.ORG - Architecture Technique

Ce document détaille l'architecture logicielle, la structure de la base de données et les choix techniques structurants du projet DISPARUS.ORG.

---

## 1. Stack Technologique

### Backend
*   **Langage :** Python 3.10+
*   **Framework Web :** Flask 3.1.2 (Architecture Blueprints)
*   **Serveur WSGI :** Gunicorn 23.0.0 (Production)
*   **ORM :** SQLAlchemy (via Flask-SQLAlchemy)
*   **Asynchronisme :** `aiohttp` (pour appels API externes non-bloquants) + `asgiref`
*   **Traitement Image :** Pillow (PIL)
*   **Génération PDF :** ReportLab
*   **Sécurité :** `werkzeug.security` (Argon2/PBKDF2), `flask-wtf` (CSRF)

### Frontend
*   **Moteur de Template :** Jinja2 (intégré à Flask)
*   **Framework CSS :** Tailwind CSS (utilisé via CDN ou build process externe selon config)
*   **JavaScript :** Vanilla JS (ES6+) pour l'interactivité (Map, Upload, Modales)
*   **Cartographie :** Leaflet.js / OpenStreetMap (supposé via les templates)

### Base de Données
*   **SGBD :** SQLite (Production légère) ou PostgreSQL (Production heavy - support via `psycopg2-binary`)
*   **Moteur de Recherche :** SQLite FTS5 (Full-Text Search)
*   **Migration :** Scripts Python idempotents (`init_db.py`)

---

## 2. Structure du Projet

L'application suit une architecture modulaire basée sur les Blueprints Flask :

```
/
├── app.py              # Application Factory (create_app)
├── main.py             # Point d'entrée WSGI
├── models/             # Définitions SQLAlchemy (MVC - Model)
│   ├── disparus.py     # Coeur du métier
│   ├── user.py         # RBAC
│   └── ...
├── routes/             # Contrôleurs (MVC - Controller)
│   ├── public.py       # Front-office
│   ├── admin.py        # Back-office
│   └── api.py          # API JSON (interne/externe)
├── services/           # Logique métier complexe
│   └── moderation.py   # Service de modération async
├── templates/          # Vues HTML (MVC - View)
├── static/             # Assets (CSS, JS, Img)
├── utils/              # Helpers techniques
│   ├── pdf_gen.py      # Moteur de génération PDF/Social
│   └── i18n.py         # Gestion des langues
└── lang/               # Fichiers de traduction JSON
```

---

## 3. Modèle de Données (Schéma Simplifié)

### `disparus_flask`
Table principale stockant les fiches de disparus.
*   **Clés :** `id` (PK), `public_id` (Unique, URL-friendly).
*   **Données :** `first_name`, `last_name`, `status` (Enum: missing, found, deceased...), `photo_url`.
*   **Géo :** `latitude`, `longitude`, `country`, `city`.
*   **Relations :** `contributions` (1-N).

### `contributions_flask`
Stocke les témoignages et informations.
*   **Clés :** `id` (PK), `disparu_id` (FK).
*   **Données :** `content`, `contribution_type` (sighting, info...), `status` (pending, approved).
*   **Auteur :** `contributor_name`, `contributor_email` (ou User ID si connecté).

### `users_flask` & `roles_flask`
Système RBAC (Role-Based Access Control).
*   **Roles :** Admin, Moderator, NGO, Secours, User.
*   **Permissions :** Stockées en JSON dans la table `roles_flask` pour une flexibilité maximale sans migration.

### `site_settings`
Configuration dynamique de l'application (Key-Value Store).
*   Permet de modifier le comportement (SEO, Sécurité, Limites) sans redéployer.

---

## 4. Flux de Données Critiques

### 4.1 Modération de Contenu (Async)
Pour éviter de bloquer le thread principal lors de l'upload d'une image :
1.  L'utilisateur soumet le formulaire (`POST /signaler`).
2.  Le serveur reçoit le fichier temporaire.
3.  `services/moderation.py` lance une tâche asynchrone (`async def check_image`).
4.  Appel API vers APILayer (Nudity/Violence) via `aiohttp`.
5.  Si Score > 0.6 : Le fichier est rejeté, l'utilisateur reçoit une erreur 403, et un log est créé.
6.  Si Score < 0.6 : Le fichier est sauvegardé localement et l'enregistrement DB est créé.

### 4.2 Génération de PDF
1.  Requête `GET /disparu/<id>/pdf`.
2.  Le contrôleur appelle `utils.pdf_gen.generate_missing_person_pdf`.
3.  ReportLab construit le document en mémoire (BytesIO).
    *   Téléchargement de la photo (si URL distante) ou lecture locale.
    *   Génération du QR Code à la volée.
    *   Composition de la mise en page selon le statut (Couleurs, Textes).
4.  Le fichier PDF est renvoyé en flux (`send_file`) avec les bons headers MIME.

---

## 5. Sécurité

*   **Rate Limiting :** Implémenté via décorateur `@rate_limit` sur les routes sensibles (API, Login, Signalement). Stockage en mémoire ou Redis (selon config).
*   **Injection SQL :** Prévenue par l'usage strict de l'ORM SQLAlchemy.
*   **XSS :** Échappement automatique par Jinja2 + Nettoyage des entrées.
*   **CSRF :** Tokens synchrones via Flask-WTF pour tous les formulaires d'état.
