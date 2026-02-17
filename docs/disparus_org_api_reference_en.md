# [ 🇫🇷 Français ](disparus_org_api_reference.md) | [ 🇬🇧 English ](disparus_org_api_reference_en.md)

# Disparus Org - API Reference

## Base URL
*   `https://[your-domain]/api`

## Authentication
*   For public endpoints: No authentication required.
*   For protected endpoints: Header `Authorization: Bearer <your_token>` (if implemented) or active session cookie.

## Endpoints

### 1. Disparus (Missing Persons/Animals)

#### `GET /api/disparus`
Retrieves the list of active disappearances.

*   **Parameters (Query Strings):**
    *   `q` (string, optional): Text search (name, city).
    *   `status` (string, optional): Filter by status (`disparu`, `retrouve`, `decede`).
    *   `type` (string, optional): Filter by type (`animal`, `humain`).
    *   `lat` (float, optional): Latitude for distance sorting.
    *   `lng` (float, optional): Longitude for distance sorting.
    *   `limit` (int, default 20): Number of results.
    *   `offset` (int, default 0): Pagination.

*   **Response (200 OK):**
    ```json
    {
      "count": 120,
      "results": [
        {
          "id": 1,
          "name": "Rex",
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
Retrieves full details of a disappearance.

*   **Response (200 OK):**
    ```json
    {
      "id": 1,
      "name": "Rex",
      "description": "Black Labrador...",
      "date_disappearance": "2023-10-25",
      "location": "Paris 15",
      "coords": {"lat": 48.8, "lng": 2.3},
      "contact": "0600000000"
    }
    ```
*   **Error (404 Not Found):** ID does not exist.

### 2. Statistics

#### `GET /api/stats`
Retrieves global site statistics.

*   **Response (200 OK):**
    ```json
    {
      "total_missing": 500,
      "found": 350,
      "success_rate": "70%"
    }
    ```

## Common Error Codes
*   `200`: Success.
*   `400`: Bad Request (missing parameters).
*   `401`: Unauthorized.
*   `403`: Forbidden.
*   `404`: Resource Not Found.
*   `500`: Internal Server Error.
