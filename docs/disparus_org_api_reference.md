# [ 🇫🇷 Français ](disparus_org_api_reference.md) | [ 🇬🇧 English ](disparus_org_api_reference_en.md)

# Disparus Org - Référence API

## Base URL
*   `https://[votre-domaine]/api`

## Authentification
*   Pour les endpoints publics : Aucune authentification requise.
*   Pour les endpoints protégés : Header `Authorization: Bearer <votre_token>` (si implémenté) ou session cookie active.

## Endpoints

### 1. Disparus

#### `GET /api/disparus`
Récupère la liste des disparitions actives.

*   **Paramètres (Query Strings) :**
    *   `q` (string, optionnel) : Recherche textuelle (nom, ville).
    *   `status` (string, optionnel) : Filtrer par statut (`disparu`, `retrouve`, `decede`).
    *   `type` (string, optionnel) : Filtrer par type (`animal`, `humain`).
    *   `lat` (float, optionnel) : Latitude pour le tri par distance.
    *   `lng` (float, optionnel) : Longitude pour le tri par distance.
    *   `limit` (int, défaut 20) : Nombre de résultats.
    *   `offset` (int, défaut 0) : Pagination.

*   **Réponse (200 OK) :**
    ```json
    {
      "count": 120,
      "results": [
        {
          "id": 1,
          "nom": "Rex",
          "type": "animal",
          "status": "disparu",
          "photo_url": "/static/uploads/rex.jpg",
          "distance_km": 2.5
        },
        ...
      ]
    }
    ```

#### `GET /api/disparus/<int:id>`
Récupère les détails complets d'une disparition.

*   **Réponse (200 OK) :**
    ```json
    {
      "id": 1,
      "nom": "Rex",
      "description": "Labrador noir...",
      "date_disparition": "2023-10-25",
      "lieu": "Paris 15",
      "coords": {"lat": 48.8, "lng": 2.3},
      "contact": "0600000000"
    }
    ```
*   **Erreur (404 Not Found) :** ID inexistant.

### 2. Statistiques

#### `GET /api/stats`
Récupère les statistiques globales du site.

*   **Réponse (200 OK) :**
    ```json
    {
      "total_disparus": 500,
      "retrouves": 350,
      "taux_reussite": "70%"
    }
    ```

## Codes d'Erreur Communs
*   `200` : Succès.
*   `400` : Requête invalide (paramètres manquants).
*   `401` : Non autorisé.
*   `403` : Interdit.
*   `404` : Ressource non trouvée.
*   `500` : Erreur serveur interne.
