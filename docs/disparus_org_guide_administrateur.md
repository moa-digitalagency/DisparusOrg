# DISPARUS.ORG - Guide Administrateur

Ce guide est exclusivement destiné aux administrateurs, modérateurs, ONG et services de secours ayant un accès privilégié au Back-Office de DISPARUS.ORG.

---

## 1. Accès et Rôles

L'accès à l'administration se fait via `/admin/login`.
*   **Admin :** Accès total (Utilisateurs, Rôles, Settings, Contenu).
*   **Modérateur :** Gestion des Signalements et Contributions uniquement.
*   **ONG / Secours :** Consultation avancée et Export de données.

---

## 2. Tableau de Bord (Dashboard)

Le Dashboard `/admin` offre une vue synthétique de l'activité du site.

### Indicateurs Clés
*   **Total Disparus :** Nombre total de fiches actives.
*   **Retrouvés / Décédés :** Statistiques de résolution des enquêtes.
*   **Dernières Activités :** Log des actions récentes (Création, Modification, Connexion).

### Carte Globale
La carte administrative affiche **tous** les points, y compris ceux "Flagged" (masqués au public) ou en attente de validation.
*   **Code Couleur :** Identique au public (Rouge = Disparu, Vert = Retrouvé, Gris = Décédé).

---

## 3. Gestion des Disparus

### Liste des Signalements (`/admin/disparus`)
*   **Recherche :** Filtrer par Nom, ID Public, Statut.
*   **Actions Rapides :** Voir, Editer, Supprimer.

### Édition d'une Fiche
En tant qu'administrateur, vous pouvez modifier toutes les données d'un disparu :
*   **Changer le Statut :**
    *   `missing` -> `found` (Retrouvé) : Déclenche l'affichage vert public.
    *   `missing` -> `deceased` (Décédé) : Déclenche l'affichage gris.
    *   `missing` -> `flagged` (Signalé) : Masque la fiche temporairement.
*   **Corriger les Infos :** Nom, Description, Photo (Ré-upload possible).
*   **Géolocalisation :** Ajuster manuellement les coordonnées GPS si l'adresse automatique est imprécise.

---

## 4. Modération des Contributions

Les utilisateurs peuvent soumettre des témoignages ou des informations. Selon la configuration, ces contributions doivent être validées avant publication.

### File d'Attente (`/admin/contributions`)
*   **Statut `pending` :** Contributions en attente de relecture.
*   **Action :**
    *   **Approuver :** La contribution devient visible sur la fiche publique.
    *   **Rejeter :** La contribution est archivée mais masquée.
*   **Types de Contribution :**
    *   `status_change` : Suggestion de l'utilisateur (ex: "J'ai vu qu'il a été retrouvé"). Si validé, pensez à mettre à jour le statut du disparu manuellement.

---

## 5. Gestion des Utilisateurs (`/admin/users`)

### Création de Comptes
Vous pouvez créer manuellement des comptes pour vos collaborateurs ou partenaires.
*   **Attribution de Rôle :** Sélectionnez le niveau de permission adéquat (Admin, Modérateur, etc.).
*   **Sécurité :** Les mots de passe sont hachés. L'utilisateur devra changer son mot de passe à la première connexion (si configuré).

### Rôles et Permissions (`/admin/roles`)
*   Le système RBAC permet de définir finement les droits d'accès.
*   **Permissions JSON :** Éditable directement en base pour les utilisateurs avancés (ex: `{"manage_users": true}`).

---

## 6. Configuration du Site (`/admin/settings`)

La page "Paramètres" permet de modifier le comportement du site sans redéploiement.

### Sections Critiques
*   **Sécurité :**
    *   `enable_rate_limiting` : Activer/Désactiver la protection anti-spam.
    *   `blocked_ips` : Liste noire des adresses IP malveillantes.
*   **Général :**
    *   `require_contribution_validation` : Si `true`, toutes les contributions doivent être modérées.
    *   `max_upload_size_mb` : Limite de taille des photos (ex: 5 Mo).
*   **SEO & Analytics :** Champs pour ID Google Analytics et Meta Tags globaux.
*   **PWA :** Personnalisation du nom de l'app, couleurs et icônes pour l'installation mobile.
