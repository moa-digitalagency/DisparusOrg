# [ 🇫🇷 Français ](disparus_org_technical_architecture.md) | [ 🇬🇧 English ](disparus_org_technical_architecture_en.md)

# Disparus Org - Architecture Technique

## 1. Vue d'Ensemble
*   **Langage :** Python 3.x
*   **Framework Web :** Flask
*   **Base de Données :** SQLAlchemy (support SQLite par défaut, compatible PostgreSQL).
*   **Template Engine :** Jinja2 (avec injection de configuration).
*   **Architecture :** Modulaire (Routes séparées, Modèles, Services).

## 2. Structure des Dossiers
*   `app.py` : Point d'entrée principal. Initialise l'application, la BDD, et enregistre les blueprints.
*   `models.py` : Définition des modèles de données (ORM SQLAlchemy).
    *   `User` : Utilisateurs et administrateurs.
    *   `Disparu` : Profils de disparitions.
    *   `Contribution` : Commentaires/Infos sur les disparitions.
    *   `SiteSetting` : Configuration dynamique.
    *   `Download` : Suivi des téléchargements.
*   `routes/` : Logique des contrôleurs.
    *   `api.py` : Endpoints JSON pour le frontend/apps tierces.
    *   `admin.py` : Interface d'administration (protégée).
    *   `public.py` : Pages publiques (accueil, détails, recherche).
*   `services/` : Logique métier complexe.
    *   `analytics.py` : Calculs statistiques (vues, conversions).
    *   `moderation.py` : Logique de validation de contenu (asynchrone).
*   `utils/` : Outils transverses.
    *   `pdf_gen.py` : Génération de PDF (ReportLab) et images sociales.
    *   `i18n.py` : Gestion des traductions (JSON).
*   `static/` : Assets frontend (CSS, JS, Images).
    *   `uploads/` : Stockage des photos des disparus.
*   `templates/` : Vues HTML (Jinja2).

## 3. Base de Données (Schéma Simplifié)
*   **User :** `id`, `username`, `email`, `password_hash`, `role` (admin/mod/user).
*   **Disparu :** `id`, `type` (animal/person), `status`, `nom`, `prenom`, `date_disparition`, `lieu`, `description`, `photo_url`, `user_id` (auteur).
    *   Relations : `contributions` (One-to-Many), `downloads` (One-to-Many).
*   **Contribution :** `id`, `disparu_id`, `user_id`, `content`, `date`.

## 4. Sécurité
*   **Mots de Passe :** Hachage via `werkzeug.security`.
*   **Sessions :** Gestion via `flask_login`.
*   **CSRF :** Protection globale activée.
*   **Uploads :** Validation des extensions de fichiers (images uniquement).
*   **SQL Injection :** Protection native via SQLAlchemy ORM.

## 5. Déploiement
*   **Serveur WSGI :** Gunicorn recommandé pour la prod.
*   **Proxy Inverse :** Nginx recommandé pour servir les statiques et le SSL.
*   **Variables d'Env :** Utilisation de `.env` pour les secrets (clé secrète, URL BDD).
