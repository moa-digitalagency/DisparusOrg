# Guide de Déploiement

Guide technique pour l'installation, la configuration et la mise en production de la plateforme DISPARUS.ORG.

## 1. Prérequis Système

*   **OS** : Linux (Ubuntu 20.04+ recommandé) ou macOS.
*   **Python** : Version 3.10 ou supérieure.
*   **Base de données** : PostgreSQL 14+ (Production) ou SQLite (Développement).
*   **Ressources** : 1 Go RAM, 10 Go Disque.

## 2. Installation Standard

### 2.1. Récupération du code
```bash
git clone https://github.com/votre-org/disparus.org.git
cd disparus.org
```

### 2.2. Environnement virtuel et dépendances
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2.3. Configuration (.env)
Créer un fichier `.env` à la racine :

```bash
# Production (PostgreSQL)
DATABASE_URL=postgresql://user:password@localhost:5432/disparus

# Sécurité (Clé aléatoire longue)
SESSION_SECRET=remplacer_par_une_chaine_aleatoire_securisee

# Compte Admin initial
ADMIN_USERNAME=admin
ADMIN_PASSWORD=changez_ce_mot_de_passe
```

### 2.4. Initialisation
```bash
# Création des tables
python init_db.py

# (Optionnel) Données de test
python init_db_demo.py
```

## 3. Mise en Production (Linux)

### 3.1. Serveur d'application (Gunicorn)
Ne jamais utiliser `python main.py` en production. Utilisez Gunicorn.

```bash
gunicorn --bind 0.0.0.0:5000 \
         --workers 4 \
         --threads 2 \
         --worker-class gthread \
         --access-logfile - \
         --error-logfile - \
         main:app
```

### 3.2. Service Systemd
Créer `/etc/systemd/system/disparus.service` :

```ini
[Unit]
Description=DISPARUS.ORG Gunicorn Service
After=network.target postgresql.service

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/disparus
EnvironmentFile=/var/www/disparus/.env
ExecStart=/var/www/disparus/venv/bin/gunicorn --workers 4 --bind 127.0.0.1:5000 main:app
Restart=always

[Install]
WantedBy=multi-user.target
```

### 3.3. Reverse Proxy (Nginx)
Créer `/etc/nginx/sites-available/disparus` :

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

    # Servir les fichiers statiques/uploads directement (Performance)
    location /statics {
        alias /var/www/disparus/statics;
        expires 30d;
    }

    client_max_body_size 10M;
}
```

### 3.4. SSL (HTTPS)
Sécuriser impérativement le trafic avec Certbot :
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d disparus.org
```

## 4. Maintenance

### Sauvegarde
*   **Base de données** : `pg_dump -U user disparus > backup.sql`
*   **Fichiers (Photos)** : `tar -czf uploads.tar.gz statics/uploads/`

### Mise à jour
1.  `git pull`
2.  `pip install -r requirements.txt`
3.  `python init_db.py` (Migrations automatiques)
4.  `sudo systemctl restart disparus`

## 5. Dépannage

*   **Logs Applicatifs** : `journalctl -u disparus -f`
*   **Logs Nginx** : `/var/log/nginx/error.log`
*   **Erreur 413** : Augmenter `client_max_body_size` dans Nginx.
*   **Erreur 502** : Gunicorn n'est pas démarré (vérifier `systemctl status disparus`).
