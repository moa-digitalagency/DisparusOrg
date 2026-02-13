# DISPARUS.ORG - Bible des Fonctionnalités

Ce document recense de manière exhaustive l'ensemble des fonctionnalités, mécanismes et règles métier de l'application DISPARUS.ORG. Il sert de référence absolue pour les développeurs, testeurs et administrateurs.

---

## 1. Gestion des Disparus (Core Feature)

### 1.1 Création d'un Signalement (Public & Admin)
*   **Formulaire de Signalement :** Accessible publiquement (`/signaler`) et via l'admin.
*   **Types de Disparus :**
    *   **Personne :** Champs spécifiques (Nom, Prénom, Age, Sexe, Description physique, Vêtements, Circonstances).
    *   **Animal :** Champs spécifiques (Race, Type d'animal, Nom).
*   **Géolocalisation :**
    *   Sélection du Pays et de la Ville.
    *   Calcul automatique ou saisie manuelle des coordonnées GPS (`latitude`, `longitude`).
    *   Validation de la proximité géographique lors de la recherche.
*   **Upload de Photo :**
    *   Format accepté : JPG, PNG, WEBP.
    *   Taille maximale configurable (par défaut 5 Mo).
    *   **Modération Automatique (IA) :** Analyse via API externe (APILayer) pour détecter la nudité et la violence.
        *   Seuil de confiance : > 0.6 (60%).
        *   Action : Blocage immédiat si positif + Log dans `ContentModerationLog`.
*   **Validation des Données :**
    *   Champs obligatoires (`required` HTML5 + vérification backend).
    *   Validation format date (`DD/MM/YYYY`).
*   **Statut Initial :** `missing` (Disparu) par défaut.

### 1.2 Cycle de Vie et Statuts
Les statuts sont mutuellement exclusifs et déclenchent des comportements visuels spécifiques :
*   `missing` (Disparu) : Thème **Rouge**. Affiché par défaut sur la carte et la liste.
*   `found` / `found_alive` (Retrouvé / Retrouvé vivant) : Thème **Vert**.
    *   Message "MERCI DE TOUT COEUR !" sur les images générées.
    *   Bandeau "Retrouvé" sur la fiche publique.
*   `deceased` / `found_deceased` (Décédé / Retrouvé décédé) : Thème **Gris**.
    *   Message "MERCI POUR VOTRE MOBILISATION, MALHEURESEMENT..." sur les images.
    *   Header PDF réduit (taille police 28) pour accommoder le texte.
*   `injured` (Blessé / Hospitalisé) : Thème **Orange**.
*   `flagged` (Signalé) : Masqué du public en attente de modération manuelle.

### 1.3 Fiche Détail (Public)
*   **URL Friendly :** `/disparu/<public_id>` (ID unique de 6 caractères alphanumériques).
*   **Affichage Dynamique :**
    *   Adaptation des labels selon le type (Personne/Animal) et le genre (Homme/Femme/Mâle/Femelle).
    *   Calcul de l'âge automatique ou affichage statique.
*   **Actions Utilisateur :**
    *   **Partager :** Génération d'image réseaux sociaux (voir section 3).
    *   **Imprimer :** Génération de PDF A4 (voir section 3).
    *   **Témoigner :** Formulaire de contribution (`/contribute`).
    *   **Signaler :** Formulaire de signalement d'abus (`/report`).

---

## 2. Système de Contributions et Témoignages

### 2.1 Soumission (Public)
*   **Formulaire Simplifié :** Nom, Contact (Email/Tel), Message, Localisation optionnelle.
*   **Type de Contribution :**
    *   `sighting` (Vu/Aperçu).
    *   `information` (Info générale).
    *   `status_change` (Suggestion de changement de statut).
*   **Sécurité :**
    *   Support du mode anonyme (configurable dans les Settings).
    *   Rate Limiting appliqué par IP.

### 2.2 Modération des Contributions (Admin)
*   **Workflow de Validation :**
    *   Statut par défaut : `pending`.
    *   Actions Admin : Valider (`approved`) ou Rejeter (`rejected`).
*   **Impact Public :**
    *   Seules les contributions `approved` sont visibles sur la fiche publique (optionnel selon config).
    *   L'historique des statuts est généré automatiquement via des contributions de type `status_change`.

---

## 3. Génération de Documents et Médias

### 3.1 Affiches PDF (A4)
*   **Technologie :** ReportLab (Python).
*   **Mise en Page :**
    *   En-tête bilingue (FR/EN) avec code couleur selon statut.
    *   Photo principale centrée.
    *   Détails en deux colonnes.
    *   **QR Code dynamique :** Pointant vers l'URL de la fiche publique.
    *   Pied de page avec contacts d'urgence.
*   **Logique Métier :**
    *   Gestion des valeurs nulles (remplacement par vide pour éviter les crashs).
    *   Titres traduits dynamiquement (ex: "DISPARU / MISSING").

### 3.2 Images Réseaux Sociaux (Carré/Portrait)
*   **Technologie :** Pillow (PIL) + Aiohttp (téléchargement async).
*   **Format :** Optimisé pour Facebook/Instagram/Twitter.
*   **Thèmes Visuels :**
    *   Application d'un overlay couleur (Rouge/Vert/Gris/Orange) avec transparence.
    *   Ajout automatique du texte de statut ("RETROUVÉ", "DÉCÉDÉ").
    *   Incrustation de la date de mise à jour si le statut n'est pas `missing`.
*   **Logique Grammaticale :**
    *   Distinction Personne (Féminin : "RETROUVÉE") vs Animal (Masculin : "RETROUVÉ") dans les textes générés en français.

---

## 4. Carte Interactive et Recherche

### 4.1 Moteur de Recherche
*   **Filtres Disponibles :**
    *   Nom / Prénom.
    *   Pays / Ville.
    *   Statut (Disparu, Retrouvé, etc.).
*   **Optimisation :**
    *   Utilisation de tables virtuelles FTS5 (Full-Text Search) SQLite pour la performance.
    *   Mise en cache du schéma de la base pour éviter l'inspection répétée (`_sqlite_fts_status`).

### 4.2 Carte (Admin & Public)
*   **Données :** Chargement via API `/api/disparus`.
*   **Marqueurs :** Code couleur correspondant au statut (Vert, Gris, Rouge, Orange).
*   **Clustering (Backend) :**
    *   Algorithme de hachage spatial (grille 0.5 degrés).
    *   Gestion du passage de la ligne de changement de date (Longitude +/- 180).
    *   Calcul de distance Haversine pour les recherches de proximité.

---

## 5. Administration et Back-office

### 5.1 Tableau de Bord (Dashboard)
*   **Statistiques en temps réel :**
    *   Total Disparus, Retrouvés, Décédés.
    *   Répartition par pays.
    *   Dernières activités (Logs).
*   **Authentification Admin :**
    *   Session sécurisée (`admin_logged_in`).
    *   Rôles RBAC : `admin` (Tout), `moderator` (Contenu uniquement), `ngo`, `secours`.

### 5.2 Gestion des Utilisateurs (RBAC)
*   **Rôles Définis :** Stockés en base (`roles_flask`), avec permissions JSON granulaires (`manage_users`, `moderate_content`, etc.).
*   **Actions :** Créer, Editer, Bannir, Changer le rôle.

### 5.3 Paramètres du Site (Settings)
*   **Configuration à chaud :** Pas de redémarrage nécessaire.
*   **Catégories :**
    *   **SEO :** Google Analytics ID, Meta descriptions.
    *   **Sécurité :** Rate Limit (req/min), IP Whitelist/Blacklist.
    *   **Général :** Taille max upload, Validation obligatoire des contributions.
    *   **PWA :** Nom de l'app, Couleurs, Icônes.

---

## 6. Sécurité et Infrastructure

### 6.1 Protection et Modération
*   **Rate Limiting :**
    *   Basé sur l'IP.
    *   Exemptions : Admins connectés, IPs whitelistées.
    *   Réponse : 429 Too Many Requests (JSON pour API, Page HTML pour navigateur).
*   **Filtrage IP :** Blocage complet des IPs blacklistées (403 Forbidden).
*   **CSRF Protection :** Active sur tous les formulaires POST (sauf `/api/` qui est exempté).

### 6.2 Architecture Technique
*   **Backend :** Flask (Python) avec Blueprints (`public`, `admin`, `api`).
*   **Asynchronisme :** Utilisation massive de `async/await` (Aiohttp) pour les opérations I/O (API externes, génération images) afin de ne pas bloquer le thread principal.
*   **Base de Données :**
    *   SQLite (Dev/Prod léger) avec extensions FTS5.
    *   SQLAlchemy ORM.
    *   Système de migration de schéma idempotent (`init_db.py`).
*   **Internationalization (i18n) :**
    *   Fichiers JSON (`lang/fr.json`, `lang/en.json`).
    *   Fallback automatique (FR -> EN si clé manquante).
    *   Support contextuel (clés `admin.*`, `detail.*`, `pdf.*`).

### 6.3 PWA (Progressive Web App)
*   **Manifest Dynamique :** Généré selon les réglages en base de données.
*   **Service Worker :** Prêt pour le cache et le mode hors-ligne (si activé).
