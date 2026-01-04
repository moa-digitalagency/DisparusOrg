# API Reference

Documentation des endpoints API de DISPARUS.ORG.

## Base URL

```
https://disparus.org/api
```

## Rate Limiting

Toutes les routes API sont protegees par un systeme de limitation :
- Par defaut : 60 requetes par minute
- Configurable dans les parametres du site

En cas de depassement, l'API retourne :
```json
{
  "error": "Rate limit exceeded",
  "retry_after": 60
}
```

## Endpoints

### Liste des personnes disparues

```
GET /api/disparus
```

Retourne la liste des personnes disparues.

**Parametres de requete**

| Parametre | Type | Description |
|-----------|------|-------------|
| status | string | Filtrer par statut (missing, found, deceased) |
| country | string | Filtrer par pays |
| limit | integer | Nombre maximum de resultats (defaut: 100) |

**Exemple de requete**

```bash
curl "https://disparus.org/api/disparus?status=missing&country=Cameroun&limit=20"
```

**Reponse**

```json
[
  {
    "id": 1,
    "public_id": "ABC123",
    "person_type": "enfant",
    "first_name": "Jean",
    "last_name": "Dupont",
    "age": 12,
    "sex": "Homme",
    "country": "Cameroun",
    "city": "Douala",
    "physical_description": "Taille 1m45, cheveux courts",
    "photo_url": "/statics/uploads/photo.jpg",
    "disappearance_date": "2025-12-20T14:30:00",
    "circumstances": "Disparu en rentrant de l'ecole",
    "latitude": 4.0511,
    "longitude": 9.7679,
    "clothing": "Uniforme scolaire bleu",
    "objects": "Sac a dos rouge",
    "contacts": [
      {
        "name": "Marie Dupont",
        "phone": "+237 6XX XXX XXX",
        "email": "marie@example.com",
        "relation": "Mere"
      }
    ],
    "status": "missing",
    "is_flagged": false,
    "created_at": "2025-12-20T15:00:00"
  }
]
```

---

### Detail d'une personne

```
GET /api/disparus/{public_id}
```

Retourne les informations detaillees d'une personne avec ses contributions.

**Parametres de chemin**

| Parametre | Type | Description |
|-----------|------|-------------|
| public_id | string | Identifiant public de la personne (ex: ABC123) |

**Exemple de requete**

```bash
curl "https://disparus.org/api/disparus/ABC123"
```

**Reponse**

```json
{
  "id": 1,
  "public_id": "ABC123",
  "person_type": "enfant",
  "first_name": "Jean",
  "last_name": "Dupont",
  "age": 12,
  "sex": "Homme",
  "country": "Cameroun",
  "city": "Douala",
  "physical_description": "Taille 1m45, cheveux courts",
  "photo_url": "/statics/uploads/photo.jpg",
  "disappearance_date": "2025-12-20T14:30:00",
  "circumstances": "Disparu en rentrant de l'ecole",
  "latitude": 4.0511,
  "longitude": 9.7679,
  "clothing": "Uniforme scolaire bleu",
  "objects": "Sac a dos rouge",
  "contacts": [...],
  "status": "missing",
  "is_flagged": false,
  "created_at": "2025-12-20T15:00:00",
  "contributions": [
    {
      "id": 1,
      "disparu_id": 1,
      "contribution_type": "sighting",
      "details": "Vu pres du marche central",
      "latitude": 4.0520,
      "longitude": 9.7680,
      "location_name": "Marche Central",
      "observation_date": "2025-12-21T10:00:00",
      "proof_url": null,
      "person_state": "bien",
      "is_verified": false,
      "created_at": "2025-12-21T11:00:00"
    }
  ]
}
```

---

### Statistiques de la plateforme

```
GET /api/stats
```

Retourne les statistiques globales de la plateforme.

**Exemple de requete**

```bash
curl "https://disparus.org/api/stats"
```

**Reponse**

```json
{
  "total": 1250,
  "missing": 980,
  "found": 270,
  "contributions": 3450,
  "countries": 42
}
```

---

### Liste des pays

```
GET /api/countries
```

Retourne la liste des 54 pays africains couverts.

**Exemple de requete**

```bash
curl "https://disparus.org/api/countries"
```

**Reponse**

```json
[
  "Afrique du Sud",
  "Algerie",
  "Angola",
  "Benin",
  "Botswana",
  "Burkina Faso",
  ...
]
```

---

### Liste des villes d'un pays

```
GET /api/cities/{country}
```

Retourne la liste des villes pour un pays donne.

**Parametres de chemin**

| Parametre | Type | Description |
|-----------|------|-------------|
| country | string | Nom du pays |

**Exemple de requete**

```bash
curl "https://disparus.org/api/cities/Cameroun"
```

**Reponse**

```json
[
  "Yaounde",
  "Douala",
  "Garoua",
  "Bamenda",
  "Bafoussam",
  "Ngaoundere",
  "Maroua",
  "Bertoua",
  "Buea",
  "Kribi",
  "Limbe",
  "Ebolowa",
  "Nkongsamba",
  "Kumba",
  "Foumban"
]
```

---

### Recherche

```
GET /api/search
```

Recherche des personnes disparues par nom, identifiant ou ville.

**Parametres de requete**

| Parametre | Type | Description |
|-----------|------|-------------|
| q | string | Terme de recherche (minimum 2 caracteres) |

**Exemple de requete**

```bash
curl "https://disparus.org/api/search?q=Jean"
```

**Reponse**

```json
[
  {
    "id": 1,
    "public_id": "ABC123",
    "first_name": "Jean",
    "last_name": "Dupont",
    "age": 12,
    "country": "Cameroun",
    "city": "Douala",
    "status": "missing",
    ...
  },
  {
    "id": 15,
    "public_id": "XYZ789",
    "first_name": "Jean-Pierre",
    "last_name": "Mbeki",
    "age": 45,
    "country": "Gabon",
    "city": "Libreville",
    "status": "missing",
    ...
  }
]
```

---

## Codes de reponse

| Code | Description |
|------|-------------|
| 200 | Requete reussie |
| 404 | Ressource non trouvee |
| 429 | Limite de requetes depassee |
| 500 | Erreur serveur |

## Format des dates

Toutes les dates sont au format ISO 8601 :
```
YYYY-MM-DDTHH:MM:SS
```

Exemple : `2025-12-20T14:30:00`

## Types de contribution

| Valeur | Description |
|--------|-------------|
| sighting | Observation de la personne |
| information | Information sur la disparition |
| found | Personne retrouvee |
| other | Autre type de contribution |

## Statuts des personnes

| Valeur | Description |
|--------|-------------|
| missing | Personne toujours disparue |
| found | Personne retrouvee |
| deceased | Personne decedee |

## Types de personnes

| Valeur | Description |
|--------|-------------|
| enfant | Moins de 18 ans |
| adulte | 18 a 59 ans |
| personne_agee | 60 ans et plus |
