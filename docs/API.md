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

---

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
| lat | float | Latitude pour tri par proximite |
| lng | float | Longitude pour tri par proximite |

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
        "email": "contact@famille.org",
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

### Personnes a proximite

```
GET /api/disparus/nearby
```

Retourne la liste des personnes disparues triees par distance depuis une position donnee.

**Parametres de requete (obligatoires)**

| Parametre | Type | Description |
|-----------|------|-------------|
| lat | float | Latitude de reference |
| lng | float | Longitude de reference |

**Parametres de requete (optionnels)**

| Parametre | Type | Description |
|-----------|------|-------------|
| limit | integer | Nombre maximum de resultats (defaut: 50) |
| country | string | Filtrer par pays |

**Exemple de requete**

```bash
curl "https://disparus.org/api/disparus/nearby?lat=33.5731&lng=-7.5898&limit=10"
```

**Reponse**

```json
[
  {
    "id": 5,
    "public_id": "XYZ789",
    "first_name": "Ahmed",
    "last_name": "Benali",
    "distance_km": 2.3,
    ...
  }
]
```

La reponse inclut un champ `distance_km` indiquant la distance en kilometres depuis la position de reference.

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
  "gender": "M",
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
  "view_count": 156,
  "created_at": "2025-12-20T15:00:00",
  "contributions": [
    {
      "id": 1,
      "disparu_id": 1,
      "contribution_type": "seen",
      "details": "Vu pres du marche central",
      "latitude": 4.0520,
      "longitude": 9.7680,
      "location_name": "Marche Central",
      "observation_date": "2025-12-21T10:00:00",
      "proof_url": null,
      "person_state": "bien",
      "is_verified": false,
      "is_approved": true,
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
  "deceased": 45,
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
  "Burundi",
  "Cameroun",
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
  }
]
```

---

## Routes SEO

### Sitemap XML

```
GET /sitemap.xml
```

Retourne le sitemap XML dynamique de la plateforme.

**Contenu**
- Pages statiques (accueil, recherche, signaler)
- Toutes les fiches de personnes (missing, found)
- Mise a jour quotidienne (`changefreq: daily`)
- Priorite 0.8 pour pages principales, 0.7 pour fiches

**Exemple de reponse**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
  <url>
    <loc>https://disparus.org/</loc>
    <lastmod>2026-01-22</lastmod>
    <changefreq>daily</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://disparus.org/disparu/ABC123</loc>
    <lastmod>2026-01-20</lastmod>
    <changefreq>daily</changefreq>
    <priority>0.7</priority>
  </url>
</urlset>
```

---

### Robots.txt

```
GET /robots.txt
```

Retourne le fichier robots.txt dynamique.

**Contenu**
- Autorise tous les robots standards
- Autorise les robots IA (GPTBot, ChatGPT-User, Google-Extended, Anthropic-AI, ClaudeBot)
- Bloque les pages admin, API et moderation

**Exemple de reponse**

```
User-agent: *
Allow: /

User-agent: GPTBot
Allow: /

User-agent: ChatGPT-User
Allow: /

Disallow: /admin/
Disallow: /api/
Disallow: /moderation

Sitemap: https://disparus.org/sitemap.xml
```

---

## Routes de telechargement

### Fiche PDF

```
GET /disparu/{public_id}/pdf
```

Telecharge la fiche complete au format PDF avec :
- En-tete avec logo et titre
- Photo de la personne
- Informations d'identite
- Description physique
- Vetements
- Circonstances
- Contacts
- QR code vers la fiche en ligne

---

### Image reseaux sociaux

```
GET /disparu/{public_id}/share-image
```

Telecharge une image optimisee pour les reseaux sociaux :
- Format : PNG 1080x1350px (portrait)
- En-tete rouge avec message d'appel
- Photo centree
- Informations de la personne
- Bloc contact
- Lien vers la fiche

---

### QR Code

```
GET /disparu/{public_id}/qrcode
```

Telecharge un QR code pointant vers la fiche en ligne.
- Format : PNG 200x200px
- Encodage : URL de la fiche

---

## Codes de reponse

| Code | Description |
|------|-------------|
| 200 | Requete reussie |
| 400 | Parametres manquants ou invalides |
| 404 | Ressource non trouvee |
| 429 | Limite de requetes depassee |
| 500 | Erreur serveur |

---

## Format des dates

Toutes les dates sont au format ISO 8601 :
```
YYYY-MM-DDTHH:MM:SS
```

Exemple : `2025-12-20T14:30:00`

---

## Types de contribution

| Valeur | Description |
|--------|-------------|
| seen | Observation de la personne |
| info | Information importante |
| police | Signalement aux autorites |
| found | Personne retrouvee |
| other | Autre type de contribution |

---

## Statuts des personnes

| Valeur | Affichage FR | Affichage EN |
|--------|-------------|--------------|
| missing | Porte(e) Disparu(e) | Missing |
| found | Retrouve(e) | Found |
| deceased | Decede(e) | Deceased |

---

## Types de personnes

| Valeur | Description |
|--------|-------------|
| enfant | Moins de 18 ans |
| adulte | 18 a 59 ans |
| personne_agee | 60 ans et plus |

---

## Exemples d'integration

### Python

```python
import requests

# Liste des personnes disparues
response = requests.get('https://disparus.org/api/disparus', params={
    'status': 'missing',
    'country': 'Maroc',
    'limit': 10
})
disparus = response.json()

# Detail d'une personne
response = requests.get('https://disparus.org/api/disparus/ABC123')
person = response.json()

# Recherche
response = requests.get('https://disparus.org/api/search', params={'q': 'Ahmed'})
results = response.json()
```

### JavaScript

```javascript
// Liste des personnes disparues
fetch('https://disparus.org/api/disparus?status=missing&limit=10')
  .then(res => res.json())
  .then(data => console.log(data));

// Personnes a proximite
navigator.geolocation.getCurrentPosition(position => {
  const { latitude, longitude } = position.coords;
  fetch(`https://disparus.org/api/disparus/nearby?lat=${latitude}&lng=${longitude}`)
    .then(res => res.json())
    .then(data => console.log(data));
});
```

### cURL

```bash
# Liste des personnes disparues
curl -X GET "https://disparus.org/api/disparus?status=missing&country=Cameroun"

# Statistiques
curl -X GET "https://disparus.org/api/stats"

# Villes d'un pays
curl -X GET "https://disparus.org/api/cities/Senegal"
```
