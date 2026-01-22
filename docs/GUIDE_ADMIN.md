# Guide administrateur

Ce guide decrit les fonctionnalites d'administration de la plateforme DISPARUS.ORG.

## Connexion

Accedez a l'interface d'administration via :
```
https://disparus.org/admin/login
```

Identifiez-vous avec les credentials definis dans les variables d'environnement :
- `ADMIN_USERNAME` : Nom d'utilisateur administrateur
- `ADMIN_PASSWORD` : Mot de passe administrateur

---

## Tableau de bord

Le tableau de bord affiche une vue d'ensemble :

- **Statistiques globales** : Total signalements, personnes retrouvees, decedees, contributions
- **Repartition par statut** : Porte(e)s Disparu(e)s, Retrouve(e)s, Decede(e)s
- **Signalements en attente** : Contenus signales a moderer
- **Liste complete** : Tous les signalements avec actions rapides

### Actions sur les fiches

Pour chaque fiche, vous pouvez :
- **Voir la fiche** : Ouvrir la fiche publique
- **Modifier le statut** : Changer entre Disparu/Retrouve/Decede
- **Supprimer** : Supprimer definitivement la fiche

---

## Menu de navigation

L'interface d'administration est organisee en trois sections :

### Menu principal
| Page | Description |
|------|-------------|
| Tableau de bord | Vue d'ensemble et statistiques |
| Signalements | Liste de toutes les fiches avec filtres |
| Moderation | Contenus signales par les utilisateurs |
| Contributions | Temoignages et informations a valider |
| Statistiques | Metriques detaillees de la plateforme |
| Carte | Vue cartographique de tous les signalements |

### Gestion
| Page | Description |
|------|-------------|
| Utilisateurs | Gestion des comptes utilisateurs |
| Roles | Configuration des permissions |

### Systeme
| Page | Description |
|------|-------------|
| Logs d'activite | Journal de toutes les actions |
| Telechargements | Suivi des fichiers telecharges |
| Parametres | Configuration du site |
| Donnees | Export, sauvegarde, restauration |

---

## Moderation

### Signalements de contenu

La page Moderation affiche :
- **Signalements en attente** : Contenus reportes par les utilisateurs
- **Fiches signalees** : Fiches ayant ete flaggees

Pour chaque signalement, vous pouvez :
- **Conserver** : Rejeter le signalement, la fiche reste intacte
- **Supprimer** : Accepter le signalement et supprimer la fiche

### Validation des contributions

Selon la configuration (`require_contribution_validation`), les contributions peuvent necessiter une approbation :

1. Allez dans **Contributions**
2. Filtrez par statut "En attente"
3. Pour chaque contribution :
   - **Approuver** : La contribution devient visible publiquement
   - **Rejeter** : La contribution est supprimee

---

## Gestion des utilisateurs

### Creer un utilisateur

1. Allez dans **Utilisateurs**
2. Cliquez sur **Ajouter un utilisateur**
3. Remplissez les informations :
   - Email (obligatoire et unique)
   - Nom d'utilisateur
   - Mot de passe
   - Prenom et nom
   - Organisation (optionnel)
   - Role

### Roles disponibles

| Role | Description | Acces |
|------|-------------|-------|
| admin | Acces complet | Toutes les fonctionnalites |
| moderator | Moderateur | Moderation, contributions, fiches |
| ngo | ONG partenaire | Signalements, statistiques, exports |
| secours | Services de secours | Signalements, carte |
| user | Utilisateur standard | Aucun acces admin |

### Modifier un utilisateur

1. Cliquez sur **Modifier** a cote de l'utilisateur
2. Modifiez les champs souhaites
3. Pour changer le mot de passe, remplissez le champ correspondant
4. Cliquez sur **Enregistrer**

### Desactiver un compte

1. Modifiez l'utilisateur
2. Decochez **Compte actif**
3. L'utilisateur ne pourra plus se connecter

---

## Gestion des roles

### Roles systeme

Les roles systeme (admin, moderator, ngo, secours, user) ne peuvent pas etre supprimes, mais leurs permissions peuvent etre modifiees.

### Creer un role personnalise

1. Allez dans **Roles**
2. Cliquez sur **Ajouter un role**
3. Configurez :
   - **Nom technique** : Identifiant sans espaces
   - **Nom affiche** : Nom lisible
   - **Description** : Explication du role
   - **Permissions** : Cochez les permissions accordees
   - **Acces menu** : Selectionnez les pages accessibles

### Permissions disponibles

| Permission | Description |
|------------|-------------|
| manage_users | Gerer les utilisateurs |
| manage_roles | Gerer les roles |
| manage_settings | Modifier les parametres |
| manage_reports | Gerer les signalements |
| manage_contributions | Valider les contributions |
| view_logs | Voir les logs d'activite |
| view_downloads | Voir les telechargements |
| moderate_content | Moderer le contenu |
| delete_content | Supprimer du contenu |
| export_data | Exporter les donnees |

---

## Statistiques

La page Statistiques affiche :

### Vue d'ensemble
- Total des signalements
- Personnes retrouvees (nombre et pourcentage)
- Personnes decedees
- Contributions recues
- Vues totales
- Telechargements

### Repartitions
- **Par pays** : Top 10 des pays avec le plus de signalements
- **Par statut** : Graphique Porte(e)s Disparu(e)s / Retrouve(e)s / Decede(e)s
- **Par ville** : Top 10 des villes

### Engagement
- **Fiches les plus vues** : Top 5 des consultations
- **Fiches les plus telechargees** : Top 5 des PDF
- **Types de telechargement** : Repartition PDF/Images/QR codes
- **Telechargements par pays** : Origine geographique

---

## Carte interactive

La page Carte affiche tous les signalements sur une carte avec :

- **Filtre par pays** : Menu deroulant pour filtrer (sauvegarde automatique)
- **Marqueurs** : Chaque signalement avec popup d'information
- **Zoom automatique** : Geolocalisation de l'utilisateur

---

## Logs d'activite

Le journal d'activite enregistre toutes les actions sur la plateforme.

### Filtres disponibles

- **Type d'action** : auth, view, create, update, delete, download, security, admin
- **Severite** : debug, info, warning, error, critical
- **Evenements securite** : Filtrer uniquement les evenements critiques
- **Recherche** : Par nom d'utilisateur, action, IP ou cible

### Informations enregistrees

Pour chaque action :
- Date et heure
- Utilisateur (ou "visiteur" pour les anonymes)
- Action effectuee
- Cible (type et nom)
- Adresse IP
- Severite

### Evenements de securite

Les evenements marques comme "securite" incluent :
- Connexions reussies et echouees
- Modifications de parametres
- Suppressions de contenu
- Tentatives de rate limiting

---

## Telechargements

Suivi de tous les fichiers telecharges :

- **Fiche concernee** : Quelle personne
- **Type de fichier** : PDF, PNG, etc.
- **Type de telechargement** : Fiche PDF, image partage, QR code
- **Date**
- **Origine** : Adresse IP et pays

---

## Gestion des donnees

La page **Donnees** permet de gerer les donnees de la plateforme.

### Exporter les donnees

Exportez les signalements au format JSON ou CSV :

1. Selectionnez le format (JSON ou CSV)
2. Optionnel : selectionnez un pays specifique
3. Cliquez sur **Exporter**

Le fichier sera telecharge avec toutes les informations des fiches.

### Sauvegarder la base

Creez une sauvegarde complete de la base de donnees :

1. Cliquez sur **Creer une sauvegarde**
2. Un fichier JSON sera telecharge avec :
   - Toutes les fiches de disparus
   - Toutes les contributions
   - Les parametres du site

### Restaurer une sauvegarde

Restaurez une sauvegarde precedente :

1. Selectionnez le fichier JSON de sauvegarde
2. Cliquez sur **Restaurer**
3. Confirmez l'operation

Les donnees existantes seront conservees, seules les nouvelles seront ajoutees.

### Supprimer des donnees

Supprimez toutes les donnees d'un pays specifique :

1. Selectionnez le pays dans le menu deroulant
2. Cliquez sur **Supprimer**
3. Confirmez l'operation (irreversible)

### Donnees de demonstration

Pour les tests et demonstrations :

- **Generer les donnees demo** : Cree 8 profils de test (Maroc + Gabon)
- **Supprimer les donnees demo** : Supprime les profils de demonstration

---

## Parametres

### Parametres generaux

| Parametre | Description |
|-----------|-------------|
| site_name | Nom du site affiche |
| site_description | Description du site |
| contact_email | Email de contact |
| site_logo | Logo du site (upload) |
| favicon | Icone du navigateur (upload) |
| placeholder_male | Image placeholder pour hommes sans photo |
| placeholder_female | Image placeholder pour femmes sans photo |

### Parametres SEO

| Parametre | Description |
|-----------|-------------|
| seo_title | Titre pour les moteurs de recherche |
| seo_description | Meta description |
| seo_keywords | Mots-cles |
| seo_og_image | Image pour les reseaux sociaux |
| seo_robots | Directive robots |
| seo_canonical_url | URL canonique (https://disparus.org) |
| seo_google_analytics | ID Google Analytics |
| seo_google_tag_manager | ID Google Tag Manager |
| seo_head_scripts | Scripts a inserer dans <head> |
| seo_body_scripts | Scripts a inserer avant </body> |

### Parametres de securite

| Parametre | Description |
|-----------|-------------|
| enable_rate_limiting | Activer la limitation de requetes |
| rate_limit_per_minute | Nombre max de requetes par minute |
| blocked_ips | Liste des IPs bloquees (JSON) |
| enable_ip_logging | Enregistrer les adresses IP |
| max_upload_size_mb | Taille max des uploads en Mo |

### Parametres de contenu

| Parametre | Description |
|-----------|-------------|
| require_contribution_validation | Contributions doivent etre validees |
| allow_anonymous_reports | Autoriser les signalements anonymes |

---

## Bonnes pratiques

### Moderation

1. **Reagissez rapidement** : Les signalements doivent etre traites dans les 24h
2. **Documentez vos decisions** : Utilisez les notes pour expliquer vos choix
3. **Verifiez les doublons** : Avant de valider une fiche, verifiez qu'elle n'existe pas deja

### Securite

1. **Verifiez les logs regulierement** : Surtout les evenements de securite
2. **Bloquez les IPs suspectes** : En cas d'abus, ajoutez les IPs a la liste de blocage
3. **Changez le mot de passe admin** : Regulierement, et surtout apres un incident

### Donnees

1. **Sauvegardez regulierement** : Base de donnees et fichiers uploades
2. **Nettoyez les fiches obsoletes** : Fiches de personnes retrouvees depuis longtemps
3. **Verifiez les contributions** : Les contributions non verifiees peuvent contenir des erreurs

### SEO

1. **Configurez l'URL canonique** : Utilisez https://disparus.org
2. **Ajoutez Google Analytics** : Pour suivre le trafic
3. **Verifiez le sitemap** : Accessible a /sitemap.xml

---

## Deconnexion

Cliquez sur **Deconnexion** dans le menu pour terminer votre session. La session expire automatiquement apres une periode d'inactivite.
