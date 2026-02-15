# API Reference

Documentation technique des endpoints API de la plateforme DISPARUS.ORG.

## Généralités

**Base URL**
```
https://disparus.org/api
```

**Authentification**
Les routes publiques sont ouvertes. Les routes protégées nécessitent un cookie de session (non documenté ici car réservé au frontend).

**Rate Limiting**
Limitation par IP :
*   60 requêtes / minute (Lecture)
*   10 requêtes / heure (Écriture/Signalement)
*   Code retour : `429 Too Many Requests`

## Endpoints de Lecture

### 1. Liste des disparus
`GET /api/disparus`

Récupère la liste filtrée des signalements.

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `status` | string | Non | Filtre par statut (`missing`, `found`, `deceased`) |
| `country` | string | Non | Nom du pays |
| `limit` | int | Non | Limite de résultats (Défaut: 100) |
| `lat` | float | Non | Latitude (pour tri géographique) |
| `lng` | float | Non | Longitude (pour tri géographique) |

**Exemple de réponse**
```json
[
  {
    "id": 123,
    "public_id": "XY789Z",
    "person_type": "child",
    "sex": "male",
    "first_name": "Moussa",
    "last_name": "Diop",
    "country": "Senegal",
    "city": "Dakar",
    "photo_url": "/static/uploads/...",
    "distance": 5.2
  }
]
```
*(Le champ `distance` n'est présent que si `lat` et `lng` sont fournis)*

### 2. Disparus à proximité
`GET /api/disparus/nearby`

Recherche optimisée par rayon géographique.

| Paramètre | Type | Requis | Description |
|-----------|------|--------|-------------|
| `lat` | float | Oui | Latitude centrale |
| `lng` | float | Oui | Longitude centrale |
| `status` | string | Non | Statut (Défaut: `missing`) |
| `limit` | int | Non | Nombre max de résultats |

### 3. Détail d'une fiche
`GET /api/disparus/<public_id>`

Récupère toutes les données d'un disparu, y compris les contributions publiques.

**Réponse**
```json
{
  "public_id": "XY789Z",
  "person_type": "child",
  "first_name": "Moussa",
  ...
  "contributions": [
    {
      "contribution_type": "seen",
      "details": "Aperçu près de la gare...",
      "created_at": "2023-10-15T14:30:00"
    }
  ]
}
```

### 4. Recherche Textuelle
`GET /api/search?q=<terme>`

Recherche sur `first_name`, `last_name`, `public_id`, et `city`.
Minimun 2 caractères.

### 5. Géolocalisation IP
`GET /api/geo/ip`

Estime la localisation de l'utilisateur basée sur son IP.

**Réponse**
```json
{
  "country": "Cameroun",
  "city": "Yaoundé",
  "ip": "102.xxx.xxx.xxx"
}
```

### 6. Données de référence
*   `GET /api/stats` : Compteurs globaux (Total, Retrouvés, Pays...).
*   `GET /api/countries` : Liste des pays ayant au moins un signalement.
*   `GET /api/cities/<country>` : Liste des villes référencées pour un pays.

## Valeurs de Référence

**Types de Personne (`person_type`)**
*   `child` : Enfant (< 18 ans)
*   `teenager` : Adolescent
*   `adult` : Adulte
*   `elderly` : Personne âgée
*   `animal` : Animal de compagnie

**Sexe (`sex`)**
*   `male`
*   `female`
*   `unknown`

**Statuts (`status`)**
*   `missing` : Disparu (Actif)
*   `found` : Retrouvé (En vie sauf indication contraire)
*   `deceased` : Décédé
*   `found_alive` : Retrouvé en vie (Précision)
*   `found_deceased` : Retrouvé décédé (Précision)

## SEO et Fichiers

*   `/sitemap.xml` : Indexation dynamique.
*   `/robots.txt` : Règles d'indexation.
*   `/disparu/<id>/pdf` : Génération PDF.
*   `/disparu/<id>/qrcode` : Génération QR Code PNG.
