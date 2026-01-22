# Fonctionnalites detaillees

Ce document decrit en detail chaque fonctionnalite de la plateforme DISPARUS.ORG.

---

## 1. Signalement de disparition

### Formulaire multi-sections

Le formulaire de signalement est divise en 4 sections distinctes pour faciliter la saisie :

#### Section 1 : Identite
- **Type de personne** : Selection parmi enfant (0-17 ans), adulte (18-59 ans), personne agee (60+)
- **Prenom et nom** : Champs obligatoires
- **Age** : Nombre entier
- **Sexe** : Homme ou Femme (utilise pour les accords grammaticaux)
- **Photo** : Upload avec validation (png, jpg, gif, webp, max 10 Mo)

#### Section 2 : Localisation
- **Pays** : Liste deroulante des 54 pays africains
- **Ville** : Liste dynamique selon le pays selectionne (650+ villes)
- **Date et heure de disparition** : Champ datetime
- **Position GPS** : Carte cliquable avec marqueur deplacable
- **Geolocalisation** : Bouton pour detecter automatiquement la position

#### Section 3 : Description
- **Description physique** : Taille, poids, couleur cheveux, signes distinctifs
- **Vetements portes** : Description des habits au moment de la disparition
- **Objets** : Sac, telephone, bijoux, etc.
- **Circonstances** : Contexte de la disparition

#### Section 4 : Contacts
- Jusqu'a 3 contacts avec pour chacun :
  - Nom
  - Telephone (avec indicatif pays)
  - Email (optionnel)
  - Lien avec la personne (pere, mere, ami...)

### Identifiant unique

Chaque signalement recoit un identifiant public unique de 6 caracteres (ex: ABC123) compose de lettres majuscules et chiffres. Cet identifiant permet de retrouver facilement une fiche.

---

## 2. Recherche et filtres

### Barre de recherche

La recherche fonctionne sur :
- Prenom et nom
- Identifiant public
- Ville
- Pays

### Filtres avances

| Filtre | Options |
|--------|---------|
| Statut | Tous / Porte(e) Disparu(e) / Retrouve(e) / Decede(e) |
| Type | Tous / Enfant / Adulte / Personne agee |
| Pays | Liste des 54 pays |
| Avec photo | Oui / Non |

### Tri par proximite

Lorsque la geolocalisation est activee, les resultats sont tries par distance depuis la position de l'utilisateur. L'endpoint `/api/disparus/nearby` utilise la formule de Haversine pour calculer les distances.

### Filtre par pays (persistant)

Un menu deroulant sur la page d'accueil et la carte admin permet de filtrer par pays. Le choix est sauvegarde dans le localStorage du navigateur.

---

## 3. Fiche de personne disparue

### Informations affichees

- Photo avec fallback vers placeholder configurable
- Identifiant public
- Statut avec badge colore
- Prenom et nom
- Age et sexe
- Pays et ville
- Date et heure de disparition
- Description physique
- Vetements portes
- Circonstances
- Objets
- Liste des contacts
- Nombre de vues

### Compteur de temps

Pour les personnes avec statut "missing" et une date de disparition, un compteur affiche :
- Nombre de jours
- Nombre d'heures
- Nombre de minutes

Le compteur se met a jour automatiquement toutes les 60 secondes via JavaScript.

### Carte interactive

- Marqueur sur le lieu de disparition
- Marqueurs pour chaque contribution avec localisation
- Zoom niveau 20 pour un maximum de detail
- Controles de zoom et plein ecran

### Historique des contributions

Liste chronologique des contributions approuvees avec :
- Type de contribution
- Date
- Details
- Lieu d'observation (si indique)
- Etat de la personne observee

---

## 4. Telechargements

### Fiche PDF

Genere avec ReportLab, le PDF inclut :
- En-tete rouge avec logo et titre
- Photo de la personne (ou placeholder)
- Informations d'identite
- Description physique
- Section vetements
- Circonstances
- Contacts
- QR code vers la fiche en ligne
- Pied de page avec URL

Format : A4 portrait

### Image reseaux sociaux

Generee avec Pillow, l'image inclut :
- Format portrait 1080x1350 pixels
- Bandeau rouge avec message d'appel
- Photo centree
- Nom et age
- Ville et pays
- Date de disparition
- Bloc contact
- Lien vers la fiche

Pas de QR code sur l'image sociale.

### QR Code

Genere avec la bibliotheque qrcode :
- Format PNG 200x200 pixels
- Encodage : URL complete de la fiche

---

## 5. Partage

### Popup de partage

Accessible via le bouton "Partager" sur chaque fiche, le popup propose 12 plateformes :

| Plateforme | Type |
|------------|------|
| Copier le lien | Presse-papier |
| SMS | Message texte |
| WhatsApp | Messagerie |
| WhatsApp Business | Messagerie pro |
| Facebook | Reseau social |
| X (Twitter) | Reseau social |
| LinkedIn | Reseau professionnel |
| Telegram | Messagerie |
| Email | Courrier electronique |
| Messenger | Messagerie Facebook |
| Viber | Messagerie |
| Pinterest | Reseau d'images |

### Message pre-rempli

Chaque partage inclut automatiquement :
- "AIDEZ-NOUS A RETROUVER CETTE PERSONNE!"
- Nom complet de la personne
- Lien vers la fiche

### Meta Open Graph

Les pages de detail ont des balises OG personnalisees :
- `og:title` : "AIDEZ-NOUS A RETROUVER CETTE PERSONNE!"
- `og:description` : "[Nom] disparu(e) le [date] a [heure] a [ville], [pays]"
- `og:type` : "article"
- `og:image` : Image configuree dans les parametres

---

## 6. Contributions

### Types de contribution

| Type | Code | Description |
|------|------|-------------|
| Vu la personne | seen | Observation de la personne |
| Info importante | info | Information utile |
| Signale police | police | Signalement aux autorites |
| Personne retrouvee | found | La personne a ete retrouvee |
| Autre | other | Autre type d'information |

### Informations collectees

- Details (texte libre)
- Localisation (carte cliquable)
- Nom du lieu
- Date d'observation
- Etat de la personne observee
- Photo de preuve (optionnelle)
- Circonstances du retour (si type "found")
- Coordonnees du contributeur (nom, telephone, email)

### Validation

Selon la configuration (`require_contribution_validation`) :
- Si active : les contributions sont en attente jusqu'a validation par un moderateur
- Si desactivee : les contributions sont visibles immediatement

---

## 7. Moderation

### Signalement de contenu

Les utilisateurs peuvent signaler une fiche pour :
- Information fausse
- Contenu inapproprie
- Doublon
- Spam

Le signalement cree un enregistrement `ModerationReport` et marque la fiche comme `is_flagged = True`.

### Interface de moderation

Les moderateurs voient :
- Liste des signalements en attente
- Details de chaque signalement (raison, date, contact)
- Actions : Conserver / Supprimer

### Validation des contributions

Interface dediee pour :
- Voir toutes les contributions en attente
- Approuver (visible publiquement)
- Rejeter (supprimee)

---

## 8. Administration

### Tableau de bord

Statistiques en temps reel :
- Total des signalements
- Porte(e)s Disparu(e)s / Retrouve(e)s / Decede(e)s
- Contributions
- Signalements en attente
- Pays couverts

### Gestion des fiches

Pour chaque fiche :
- Voir la fiche publique
- Modifier le statut
- Supprimer (avec confirmation)

### Gestion des utilisateurs

CRUD complet avec :
- Email unique
- Nom d'utilisateur
- Mot de passe (hashage automatique)
- Role
- Organisation
- Statut actif/inactif

### Gestion des roles

4 roles systeme non supprimables :
- admin : Acces complet
- moderator : Moderation et contributions
- ngo : Signalements et statistiques
- secours : Signalements et carte

Chaque role a :
- Permissions specifiques
- Acces aux menus configurable

### Journalisation

Enregistrement automatique de :
- Toutes les connexions (reussies et echouees)
- Actions CRUD sur les fiches
- Telechargements
- Modifications de parametres
- Evenements de securite

Filtres : type, severite, utilisateur, IP, date

### Telechargements

Suivi de chaque telechargement :
- Fiche concernee
- Type (PDF, image, QR)
- Date
- IP et pays d'origine

### Gestion des donnees

- Export JSON/CSV (tout ou par pays)
- Sauvegarde complete
- Restauration
- Suppression par pays
- Gestion des donnees de demonstration

---

## 9. SEO et referencement

### Sitemap XML

Route `/sitemap.xml` generee dynamiquement :
- Pages statiques (accueil, recherche, signaler)
- Toutes les fiches (missing, found)
- Frequence : daily
- Priorite : 1.0 (accueil), 0.8 (pages), 0.7 (fiches)

### Robots.txt

Route `/robots.txt` generee dynamiquement :
- Autorise tous les robots standards
- Autorise les robots IA (GPTBot, ChatGPT-User, Google-Extended, Anthropic-AI, ClaudeBot)
- Bloque : /admin/, /api/, /moderation

### Configuration SEO

Via l'interface admin :
- Titre SEO
- Meta description
- Mots-cles
- Image OpenGraph
- URL canonique
- Google Analytics
- Google Tag Manager
- Scripts personnalises (head et body)

---

## 10. PWA (Progressive Web App)

### Manifest

Fichier `/manifest.json` avec :
- Nom de l'application
- Description
- Icones
- Couleurs
- Mode d'affichage (standalone)

### Service Worker

Fichier `/sw.js` avec :
- Cache des pages visitees
- Fonctionnement offline
- Synchronisation au retour de connexion

### Installation

Possibilite d'installer l'application sur :
- Ecran d'accueil mobile
- Bureau desktop

---

## 11. Internationalisation

### Langues supportees

- Francais (fr) - par defaut
- Anglais (en)

### Gestion de la langue

- Selection via le menu en haut de page
- Stockage dans un cookie
- Detection automatique selon le navigateur

### Labels de statut

| Code | Francais | Anglais |
|------|----------|---------|
| missing | Porte(e) Disparu(e) | Missing |
| found | Retrouve(e) | Found |
| deceased | Decede(e) | Deceased |

Les labels respectent le genre (M/F) de la personne.

---

## 12. Securite

### Authentification

- Basee sur les variables d'environnement (ADMIN_USERNAME, ADMIN_PASSWORD)
- Sessions Flask avec cle secrete
- Expiration automatique des sessions

### Rate limiting

- Configurable (requetes par minute)
- Applique sur les endpoints API
- Retourne 429 en cas de depassement

### Validation des uploads

- Extensions autorisees : png, jpg, jpeg, gif, webp
- Verification du type MIME
- Noms de fichiers securises
- Taille maximale configurable

### Journalisation

- Enregistrement des IPs
- Evenements de securite marques
- Niveaux de severite (debug, info, warning, error, critical)

---

## 13. Cartographie

### Bibliotheque

Leaflet avec tuiles OpenStreetMap

### Fonctionnalites

- Marqueurs personnalises selon le statut
- Popups avec photo et informations
- Zoom et navigation
- Geolocalisation automatique
- Zoom niveau 20 sur les fiches

### Pages avec carte

- Accueil : Tous les signalements
- Fiche : Lieu de disparition + contributions
- Admin carte : Vue complete avec filtres

---

## 14. API REST

### Endpoints publics

| Methode | Route | Description |
|---------|-------|-------------|
| GET | /api/disparus | Liste des personnes |
| GET | /api/disparus/nearby | Liste triee par proximite |
| GET | /api/disparus/{id} | Detail d'une personne |
| GET | /api/stats | Statistiques |
| GET | /api/countries | Liste des pays |
| GET | /api/cities/{country} | Villes d'un pays |
| GET | /api/search | Recherche |

### Format

Toutes les reponses sont en JSON avec les dates au format ISO 8601.

### Protection

Rate limiting configurable sur tous les endpoints API.
