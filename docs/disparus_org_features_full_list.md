# [ 🇫🇷 Français ](disparus_org_features_full_list.md) | [ 🇬🇧 English ](disparus_org_features_full_list_en.md)

# Disparus Org - Liste Complète des Fonctionnalités

## 1. Gestion des Disparitions (Disparus)
*   **Création de Profil :** Formulaire complet pour signaler une disparition (humain ou animal).
    *   Champs : Nom, prénom (pour humains), type (Animal/Humain), statut (Disparu/Retrouvé/Décédé/Blessé), date, lieu (géolocalisation), description, contact, photos.
    *   Validation : Champs obligatoires, formats de date, géolocalisation valide.
*   **Recherche et Filtres :**
    *   Recherche par mot-clé (nom, description).
    *   Filtres par statut, type (Animal/Humain), date.
    *   Tri par distance (géolocalisation).
*   **Affichage Détails :** Page dédiée pour chaque profil avec toutes les informations, carte de localisation, et galerie photos.
*   **Mise à jour de Statut :** Possibilité de changer le statut (ex: de Disparu à Retrouvé).

## 2. Génération de Documents (PDF & Images)
*   **Affiches PDF :** Génération automatique d'affiches "Avis de Recherche" au format A4.
    *   Contient : Photo principale, infos clés, QR code vers la fiche en ligne.
    *   Variantes : Couleurs et textes adaptés au statut (Rouge=Disparu, Vert=Retrouvé, Gris=Décédé, Orange=Blessé).
*   **Visuels Réseaux Sociaux :** Génération d'images optimisées pour le partage (Carré/Paysage).
    *   Thèmes visuels automatiques selon le statut.

## 3. Carte Interactive
*   **Affichage Global :** Carte montrant tous les signalements actifs.
*   **Clustering :** Regroupement des marqueurs proches pour la lisibilité.
*   **Filtres Carte :** Interaction avec les filtres de recherche globaux.

## 4. Espace Administration
*   **Tableau de Bord :** Vue d'ensemble des statistiques (nombre de disparus, retrouvés, etc.).
*   **Gestion des Utilisateurs :** Liste, rôles (Admin/Modérateur/Utilisateur), bannissement.
*   **Modération des Contenus :** Validation/Rejet des signalements et commentaires.
*   **Logs d'Activité :** Historique des actions (créations, modifications, suppressions).
*   **Paramètres du Site :** Configuration globale (ex: contact, réseaux sociaux).

## 5. API Rest
*   **Endpoints Publics :**
    *   `GET /api/disparus` : Liste filtrée des disparitions.
    *   `GET /api/disparus/<id>` : Détails d'un profil.
*   **Endpoints Sécurisés :** Gestion via tokens (si implémenté) ou session admin.

## 6. Sécurité & Conformité
*   **Authentification :** Login/Register sécurisé, hachage des mots de passe.
*   **Protection CSRF :** Sur tous les formulaires.
*   **Gestion des Droits :** Vérification des permissions pour l'édition/suppression.
*   **Conformité RGPD :** (À vérifier) Mention des données collectées, possibilité de suppression de compte.

## 7. Outils Divers
*   **Analytics :** Suivi basique des vues sur les profils.
*   **Internationalisation (i18n) :** Support multilingue (FR/EN) pour l'interface et les documents générés.
