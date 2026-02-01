# Manuel d'Administration

Ce document décrit les fonctionnalités de l'interface d'administration ("Back-office"), réservée aux gestionnaires de la plateforme.

## 1. Accès et Connexion

L'interface est accessible via l'URL `/admin/login`.
L'accès nécessite un compte utilisateur disposant du rôle "Admin" ou de permissions spécifiques.
*Note : Par défaut, le système requiert la configuration de la variable d'environnement `ADMIN_PASSWORD`.*

## 2. Tableau de Bord (Dashboard)

La page d'accueil de l'administration offre une vue synthétique :
*   **KPIs** : Compteurs en temps réel (Total disparus, Retrouvés, Décédés, Signalements en attente).
*   **Carte** : Visualisation globale de tous les points de disparition.
*   **Derniers Ajouts** : Liste rapide des fiches récemment créées.

## 3. Gestion des Signalements (Disparus)

Menu **"Signalements"** ou via la recherche.

### Actions Disponibles
*   **Modifier** : Édition complète de la fiche (Correction orthographe, changement photo, mise à jour localisation).
*   **Changer le Statut** : Transition d'état critique.
    *   *Missing* -> *Found* (Retrouvé)
    *   *Found* -> *Found Alive* / *Found Deceased* (Précision de l'état vital)
    *   Ce changement génère automatiquement une "Contribution" système pour l'historique.
*   **Supprimer** : Effacement définitif de la base de données.

## 4. Modération

Menu **"Modération"**.
C'est le centre de contrôle de la qualité des données.

*   **File d'attente** : Liste des signalements faits par les utilisateurs (contenu inapproprié, erreurs).
*   **Résolution** :
    *   *Ignorer/Dé-flagger* : Le signalement n'était pas justifié, la fiche est remise en état normal.
    *   *Supprimer* : Le contenu est effectivement problématique, la fiche est supprimée.

## 5. Gestion des Données

Menu **"Données"**. Outils pour la maintenance de masse.

*   **Export** : Téléchargement des données (JSON ou CSV). Utile pour des analyses externes ou archivage.
*   **Sauvegarde (Backup)** : Génération d'un fichier JSON complet contenant Fiches + Contributions + Rapports.
*   **Restauration** : Réimportation d'un fichier de sauvegarde.
*   **Suppression de masse** :
    *   Par pays : Supprime toutes les fiches d'un pays donné.
    *   Données Démo : Nettoyage rapide des données de test (IDs commençant par 'DEMO').

## 6. Statistiques

Menu **"Statistiques"**.
Outil d'analyse décisionnelle avec filtres par date (1 jour, 7 jours, 1 mois, Personnalisé).

*   **Répartition** : Humains vs Animaux.
*   **Issues** : Taux de résolution (Retrouvés vs Total).
*   **Géographie** : Classement par pays.
*   **Engagement** : Nombre de vues, nombre de téléchargements d'affiches (PDF).
*   **Exports** : Génération de rapports statistiques en PDF ou CSV.

## 7. Paramètres de la Plateforme

Menu **"Paramètres"**. Configuration à chaud sans redémarrage.

*   **Général** : Nom du site, email de contact.
*   **SEO & Apparence** : Logos, Icônes PWA, Images de partage par défaut (OG Image).
*   **Sécurité** :
    *   Activation/Désactivation du Rate Limiting.
    *   Liste noire d'IPs.
    *   Taille maximale des uploads.

## 8. Utilisateurs et Rôles

*   **Utilisateurs** : Création de comptes pour les modérateurs ou partenaires.
*   **Rôles** : Définition des permissions (RBAC). Exemple : Créer un rôle "Modérateur" qui a accès à la Modération mais pas aux Paramètres système.

## 9. Logs et Audit

Menu **"Logs"**.
Historique technique de toutes les actions (Qui a fait quoi ?).
*   Filtrage par sévérité (Info, Warning, Critical).
*   Filtrage par type d'action (Auth, Delete, Update).
*   Permet d'identifier les tentatives d'intrusion ou les erreurs de manipulation.
