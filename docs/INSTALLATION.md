# Installation et deploiement

Guide complet pour installer et deployer DISPARUS.ORG.

## Prerequis

### Systeme
- Linux (Ubuntu 20.04+ recommande) ou macOS
- Python 3.11 ou superieur
- PostgreSQL 14 ou superieur
- 512 Mo RAM minimum (1 Go recommande)
- 1 Go d'espace disque

### Outils
- pip (gestionnaire de paquets Python)
- Git

---

## Installation locale

### 1. Cloner le depot

```bash
git clone <repository-url>
cd disparus.org
```

### 2. Installer les dependances Python

```bash
pip install -r requirements.txt
```

Dependances principales :
- Flask
- Flask-SQLAlchemy
- Flask-Babel
- psycopg2-binary
- gunicorn
- reportlab
- qrcode
- Pillow
- python-dotenv
- email-validator

### 3. Configurer les variables d'environnement

Creer un fichier `.env` ou configurer les variables :

```bash
# Base de donnees
DATABASE_URL=postgresql://user:password@localhost:5432/disparus

# Session
SESSION_SECRET=votre-cle-secrete-longue-et-aleatoire

# Administration
ADMIN_USERNAME=admin
ADMIN_PASSWORD=votre-mot-de-passe-securise
```

### 4. Initialiser la base de donnees

```bash
python init_db.py
```

Ce script :
- Cree toutes les tables necessaires
- Initialise les roles par defaut (admin, moderator, ngo, secours, user)
- Configure les parametres par defaut du site
- Applique les migrations si necessaire

### 5. (Optionnel) Ajouter des donnees de demonstration

```bash
python init_db_demo.py
```

Ce script cree 8 profils de test :
- 4 au Maroc (Casablanca, Rabat, Marrakech, Fes)
- 4 au Gabon (Libreville, Port-Gentil, Franceville, Oyem)

Les images de demonstration sont situees dans `statics/uploads/demo/`.

### 6. Lancer l'application

Mode developpement :
```bash
python main.py
```

Mode production :
```bash
gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
```

L'application est accessible a : http://localhost:5000

---

## Deploiement en production

### Configuration Gunicorn recommandee

```bash
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --threads 2 \
         --worker-class gthread \
         --reuse-port \
         --access-logfile - \
         --error-logfile - \
         main:app
```

Parametres :
- `--workers 4` : 4 processus workers (ajuster selon CPU)
- `--threads 2` : 2 threads par worker
- `--worker-class gthread` : Workers multi-threades
- `--reuse-port` : Reutilisation du port pour zero-downtime

### Configuration reverse proxy (Nginx)

```nginx
server {
    listen 80;
    server_name disparus.org www.disparus.org;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /statics {
        alias /path/to/app/statics;
        expires 30d;
    }

    client_max_body_size 10M;
}
```

### HTTPS avec Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d disparus.org -d www.disparus.org
```

### Configuration systemd

Creer `/etc/systemd/system/disparus.service` :

```ini
[Unit]
Description=DISPARUS.ORG Gunicorn Service
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/disparus-org
EnvironmentFile=/var/www/disparus-org/.env
ExecStart=/var/www/disparus-org/venv/bin/gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Activer le service :
```bash
sudo systemctl enable disparus
sudo systemctl start disparus
```

---

## Configuration du site

Une fois l'application deployee, acceder a l'administration :

1. Aller sur `/admin/login`
2. Se connecter avec `ADMIN_USERNAME` et `ADMIN_PASSWORD`
3. Naviguer vers **Parametres**

### Parametres disponibles

#### General
| Parametre | Description |
|-----------|-------------|
| site_name | Nom du site (DISPARUS.ORG) |
| site_description | Description du site |
| contact_email | Email de contact |
| site_logo | Logo du site (upload) |
| favicon | Icone du navigateur (upload) |
| placeholder_male | Image par defaut pour hommes sans photo |
| placeholder_female | Image par defaut pour femmes sans photo |

#### SEO
| Parametre | Description |
|-----------|-------------|
| seo_title | Titre pour les moteurs de recherche |
| seo_description | Meta description |
| seo_keywords | Mots-cles |
| seo_og_image | Image OpenGraph pour partages |
| seo_canonical_url | URL canonique (https://disparus.org) |
| seo_google_analytics | ID Google Analytics |
| seo_google_tag_manager | ID Google Tag Manager |
| seo_head_scripts | Scripts personnalises (head) |
| seo_body_scripts | Scripts personnalises (body) |

#### Securite
| Parametre | Description |
|-----------|-------------|
| enable_rate_limiting | Activer la limitation de requetes |
| rate_limit_per_minute | Limite par minute |
| blocked_ips | Liste d'IPs bloquees (JSON) |
| enable_ip_logging | Journalisation des IPs |
| max_upload_size_mb | Taille max des uploads en Mo |

#### Contenu
| Parametre | Description |
|-----------|-------------|
| require_contribution_validation | Valider les contributions avant publication |
| allow_anonymous_reports | Autoriser les signalements anonymes |

---

## Sauvegarde et restauration

### Depuis l'interface admin

1. Aller dans **Administration > Donnees**
2. Cliquer sur **Creer une sauvegarde**
3. Le fichier JSON contient toutes les donnees

Pour restaurer :
1. Aller dans **Administration > Donnees**
2. Selectionner le fichier de sauvegarde
3. Cliquer sur **Restaurer**

### En ligne de commande

#### Base de donnees

```bash
# Sauvegarde
pg_dump -U user -d disparus > backup_$(date +%Y%m%d).sql

# Restauration
psql -U user -d disparus < backup_20260122.sql
```

#### Fichiers uploades

```bash
# Sauvegarde
tar -czf uploads_$(date +%Y%m%d).tar.gz statics/uploads/

# Restauration
tar -xzf uploads_20260122.tar.gz -C statics/
```

---

## Mise a jour

1. Sauvegarder la base de donnees
2. Arreter le service : `sudo systemctl stop disparus`
3. Mettre a jour le code : `git pull origin main`
4. Installer les nouvelles dependances : `pip install -r requirements.txt`
5. Appliquer les migrations : `python init_db.py`
6. Redemarrer le service : `sudo systemctl start disparus`

---

## Surveillance

### Logs

- Logs Gunicorn : via systemd journal (`journalctl -u disparus -f`)
- Logs d'activite : `/admin/logs` dans l'interface

### Metriques

L'interface d'administration fournit des statistiques :
- Nombre de signalements
- Personnes retrouvees
- Contributions
- Telechargements
- Visites par pays

### Alertes

Configurer une alerte sur :
- Erreurs HTTP 5xx repetees
- Base de donnees inaccessible
- Disque plein (uploads)

---

## Depannage

### Erreur de connexion base de donnees

Verifier :
- Variable `DATABASE_URL` correcte
- PostgreSQL en cours d'execution
- Firewall autorisant le port 5432

### Uploads qui echouent

Verifier :
- Permissions du dossier `statics/uploads/` (755)
- Limite de taille (`client_max_body_size` dans Nginx)
- Extensions autorisees (png, jpg, gif, webp)

### Session expiree

Verifier :
- Variable `SESSION_SECRET` definie et stable entre redemarrages
- Cookies autorises dans le navigateur

### PDF qui ne se generent pas

Verifier :
- Package `reportlab` installe
- Package `Pillow` installe
- Package `qrcode` installe

### Sitemap ou robots.txt inaccessible

Les fichiers `/sitemap.xml` et `/robots.txt` sont generes dynamiquement. Verifier :
- Le serveur Flask est bien demarre
- Pas de fichiers statiques du meme nom a la racine

---

## Variables d'environnement

| Variable | Description | Obligatoire |
|----------|-------------|-------------|
| DATABASE_URL | URL PostgreSQL | Oui |
| SESSION_SECRET | Cle de session Flask | Oui |
| ADMIN_USERNAME | Nom d'utilisateur admin | Oui |
| ADMIN_PASSWORD | Mot de passe admin | Oui |
