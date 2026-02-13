# DISPARUS.ORG - Guide de Déploiement

Ce guide détaille les procédures pour installer, configurer et déployer l'application DISPARUS.ORG en environnement local (développement) et serveur (production).

---

## 1. Prérequis Système

*   **Python :** Version 3.10 ou supérieure recommandée.
*   **Base de Données :**
    *   **Développement :** SQLite (inclus par défaut).
    *   **Production :** PostgreSQL (recommandé pour les performances FTS et la concurrence).
*   **Outils :** `pip`, `virtualenv` (ou `uv`/`poetry`), `git`.

---

## 2. Installation (Pas à Pas)

### 2.1 Clonage du Code Source
```bash
git clone https://github.com/votre-orga/disparus-org.git
cd disparus-org
```

### 2.2 Création de l'Environnement Virtuel
Il est crucial d'isoler les dépendances Python pour éviter les conflits système.
```bash
python3 -m venv venv
source venv/bin/activate  # Sur Linux/Mac
# venv\Scripts\activate   # Sur Windows
```

### 2.3 Installation des Dépendances
Le fichier `requirements.txt` contient toutes les bibliothèques nécessaires (Flask, SQLAlchemy, Pillow, ReportLab, Aiohttp...).
```bash
pip install -r requirements.txt
```

---

## 3. Configuration

L'application utilise des variables d'environnement pour sa configuration sensible. Créez un fichier `.env` à la racine ou exportez les variables dans votre shell.

### Variables Essentielles (`.env`)
```bash
# Configuration Générale
FLASK_APP=app.py
FLASK_ENV=development       # Passer à 'production' pour le déploiement réel
SECRET_KEY=votre_cle_secrete_aleatoire_et_longue # Sécurise les sessions

# Base de Données
DATABASE_URL=sqlite:///instance/disparus.db # Chemin absolu recommandé en Prod

# Compte Admin Initial (Créé au premier lancement via init_db.py)
ADMIN_PASSWORD=MonMotDePasseTresSecurise123!

# Services Tiers (Modération Automatique - Optionnel)
NUDITY_DETECTION_API_KEY=votre_cle_api_apilayer
VIOLENCE_DETECTION_API_KEY=votre_cle_api_apilayer
GEO_API_KEY=votre_cle_api_apilayer
```

---

## 4. Initialisation de la Base de Données

Avant de lancer le serveur, le schéma de base de données doit être créé. Le script `init_db.py` gère cela de manière idempotente (il ne casse pas l'existant).

```bash
python init_db.py
```
*   Ce script crée les tables.
*   Il initialise les rôles par défaut (Admin, Moderateur, User...).
*   Il crée l'utilisateur admin avec le mot de passe défini dans `ADMIN_PASSWORD`.

---

## 5. Lancement de l'Application

### En Développement
Utilisez le serveur de développement Flask (avec rechargement à chaud).
```bash
python main.py
# L'application sera accessible sur http://localhost:5000
```

### En Production (Gunicorn)
Ne jamais utiliser `python main.py` en production. Utilisez un serveur WSGI robuste comme Gunicorn.
```bash
# Exemple de commande pour lancer avec 4 workers
gunicorn -w 4 -b 0.0.0.0:8000 main:app
```
*   **Reverse Proxy :** Il est fortement recommandé de placer Nginx devant Gunicorn pour gérer le SSL (HTTPS) et les fichiers statiques.

---

## 6. Maintenance et Mises à Jour

### Sauvegarde
Pour SQLite, copiez simplement le fichier `instance/disparus.db`.
Pour PostgreSQL, utilisez `pg_dump`.

### Restauration de Données (Admin)
L'interface d'administration `/admin` propose un outil de restauration de données qui évite les doublons (N+1 queries optimisées).

### Logs
Les logs d'application sont dirigés vers la sortie standard (stdout) en configuration par défaut, ou vers des fichiers spécifiques selon la configuration de votre gestionnaire de processus (Systemd/Docker).
