# [ 🇫🇷 Français ](disparus_org_technical_architecture.md) | [ 🇬🇧 English ](disparus_org_technical_architecture_en.md)

# Disparus Org - Technical Architecture

## 1. Overview
*   **Language:** Python 3.x
*   **Web Framework:** Flask
*   **Database:** SQLAlchemy (default SQLite support, PostgreSQL compatible).
*   **Template Engine:** Jinja2 (with configuration injection).
*   **Architecture:** Modular (Separated Routes, Models, Services).

## 2. Folder Structure
*   `app.py`: Main entry point. Initializes app, DB, and registers blueprints.
*   `models.py`: Data model definitions (SQLAlchemy ORM).
    *   `User`: Users and administrators.
    *   `Disparu`: Disappearance profiles.
    *   `Contribution`: Comments/Info on disappearances.
    *   `SiteSetting`: Dynamic configuration.
    *   `Download`: Download tracking.
*   `routes/`: Controller logic.
    *   `api.py`: JSON endpoints for frontend/third-party apps.
    *   `admin.py`: Administration interface (protected).
    *   `public.py`: Public pages (home, details, search).
*   `services/`: Complex business logic.
    *   `analytics.py`: Statistical calculations (views, conversions).
    *   `moderation.py`: Content validation logic (asynchronous).
*   `utils/`: Cross-cutting tools.
    *   `pdf_gen.py`: PDF generation (ReportLab) and social images.
    *   `i18n.py`: Translation management (JSON).
*   `static/`: Frontend assets (CSS, JS, Images).
    *   `uploads/`: Storage for missing persons photos.
*   `templates/`: HTML views (Jinja2).

## 3. Database (Simplified Schema)
*   **User:** `id`, `username`, `email`, `password_hash`, `role` (admin/mod/user).
*   **Disparu:** `id`, `type` (animal/person), `status`, `last_name`, `first_name`, `date_disappearance`, `location`, `description`, `photo_url`, `user_id` (author).
    *   Relationships: `contributions` (One-to-Many), `downloads` (One-to-Many).
*   **Contribution:** `id`, `disparu_id`, `user_id`, `content`, `date`.

## 4. Security
*   **Passwords:** Hashing via `werkzeug.security`.
*   **Sessions:** Management via `flask_login`.
*   **CSRF:** Global protection enabled.
*   **Uploads:** File extension validation (images only).
*   **SQL Injection:** Native protection via SQLAlchemy ORM.

## 5. Deployment
*   **WSGI Server:** Gunicorn recommended for prod.
*   **Reverse Proxy:** Nginx recommended for serving statics and SSL.
*   **Env Variables:** Use `.env` for secrets (secret key, DB URL).
