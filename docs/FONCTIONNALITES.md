# Fonctionnalités de la Plateforme

Liste détaillée des capacités fonctionnelles de DISPARUS.ORG.

## 1. Fonctionnalités Publiques (Front-Office)

### Gestion des Disparitions
*   **Signalement Express** : Formulaire optimisé pour mobile permettant de créer une fiche en moins de 2 minutes.
*   **Support Multi-Type** : Distinction claire entre disparitions Humaines (Enfant, Adulte, Senior) et Animales.
*   **Géolocalisation** :
    *   Saisie automatique via GPS du téléphone.
    *   Sélection manuelle sur carte.
    *   Sélecteurs Pays/Ville dynamiques.
*   **Upload Photos** : Prise en charge des formats standards, redimensionnement et sécurisation.

### Recherche et Consultation
*   **Moteur de Recherche** :
    *   Recherche textuelle (Nom, Ville).
    *   *Full Text Search* (PostgreSQL uniquement) pour une pertinence accrue.
*   **Filtres Avancés** : Statut, Type, Pays, Présence de photo.
*   **Carte Interactive** : Visualisation de tous les points (Clustering pour les zones denses à venir).
*   **Fiche Détaillée** : Affichage complet (Description, Circonstances, Contacts masqués ou affichés selon config).

### Mobilisation et Partage
*   **Génération PDF** : Création à la volée d'une affiche "Alerte Disparition" (A4) avec photo et QR Code.
*   **Social Share** : Génération d'une image au format carré/paysage optimisée pour WhatsApp/Facebook.
*   **QR Code** : Génération d'un QR code unique pointant vers la fiche.
*   **Contributions** : Formulaire permettant aux tiers d'ajouter des témoignages ou observations sur une fiche existante.

## 2. Fonctionnalités d'Administration (Back-Office)

### Pilotage
*   **Dashboard** : Vue synthétique des indicateurs clés (KPIs).
*   **Carte Globale** : Vue d'ensemble de la situation géographique.

### Gestion de Contenu
*   **Édition Complète** : Modification de tous les champs d'une fiche.
*   **Workflow de Statut** : Gestion du cycle de vie (Disparu -> Retrouvé -> Clôturé).
*   **Modération** :
    *   Files d'attente des signalements abusifs.
    *   Logs de modération automatisée (images).
    *   Validation/Rejet des contributions citoyennes.

### Data Management
*   **Exports** : Données brutes en JSON ou CSV.
*   **Sauvegardes** : Système de Backup/Restore complet (Fichiers JSON).
*   **Nettoyage** : Suppression en masse par critères géo ou type.

### Analyses (Analytics)
*   **Statistiques Temporelles** : Courbes d'évolution des signalements.
*   **Analyses Géographiques** : Répartition par pays/ville.
*   **Métriques d'Engagement** : Suivi des vues et des téléchargements d'affiches.

## 3. Fonctionnalités Techniques et Sécurité

*   **Sécurité** :
    *   Protection CSRF (Cross-Site Request Forgery).
    *   Rate Limiting (Limitation du nombre de requêtes par IP) sur les formulaires critiques.
    *   Sanitisation des entrées utilisateurs (Protection XSS/Injection).
*   **SEO** :
    *   Génération automatique du `sitemap.xml`.
    *   Fichier `robots.txt` dynamique.
    *   Metatags OpenGraph dynamiques pour chaque fiche.
*   **Performance** :
    *   Mise en cache des paramètres globaux.
    *   Chargement différé (Lazy loading) des images.
