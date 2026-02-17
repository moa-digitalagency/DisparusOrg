# [ 🇫🇷 Français ](disparus_org_features_full_list.md) | [ 🇬🇧 English ](disparus_org_features_full_list_en.md)

# Disparus Org - Full Features List

## 1. Missing Persons Management (Disparus)
*   **Profile Creation:** Complete form to report a disappearance (human or animal).
    *   Fields: Last name, First name (for humans), Type (Animal/Human), Status (Missing/Found/Deceased/Injured), Date, Location (Geolocation), Description, Contact, Photos.
    *   Validation: Mandatory fields, date formats, valid geolocation.
*   **Search and Filters:**
    *   Keyword search (name, description).
    *   Filters by status, type (Animal/Human), date.
    *   Sort by distance (geolocation).
*   **Details View:** Dedicated page for each profile with full information, location map, and photo gallery.
*   **Status Update:** Ability to change status (e.g., from Missing to Found).

## 2. Document Generation (PDF & Images)
*   **PDF Posters:** Automatic generation of "Wanted" posters in A4 format.
    *   Contains: Main photo, key info, QR code to the online profile.
    *   Variants: Colors and texts adapted to status (Red=Missing, Green=Found, Gray=Deceased, Orange=Injured).
*   **Social Media Visuals:** Generation of images optimized for sharing (Square/Landscape).
    *   Automatic visual themes based on status.

## 3. Interactive Map
*   **Global View:** Map showing all active reports.
*   **Clustering:** Grouping of nearby markers for readability.
*   **Map Filters:** Interaction with global search filters.

## 4. Administration Area
*   **Dashboard:** Overview of statistics (number of missing, found, etc.).
*   **User Management:** List, roles (Admin/Moderator/User), banning.
*   **Content Moderation:** Validation/Rejection of reports and comments.
*   **Activity Logs:** History of actions (creations, modifications, deletions).
*   **Site Settings:** Global configuration (e.g., contact, social networks).

## 5. REST API
*   **Public Endpoints:**
    *   `GET /api/disparus`: Filtered list of disappearances.
    *   `GET /api/disparus/<id>`: Details of a profile.
*   **Secured Endpoints:** Management via tokens (if implemented) or admin session.

## 6. Security & Compliance
*   **Authentication:** Secure Login/Register, password hashing.
*   **CSRF Protection:** On all forms.
*   **Rights Management:** Permission verification for editing/deletion.
*   **GDPR Compliance:** (To be verified) Mention of collected data, account deletion capability.

## 7. Miscellaneous Tools
*   **Analytics:** Basic tracking of views on profiles.
*   **Internationalization (i18n):** Multilingual support (FR/EN) for the interface and generated documents.
