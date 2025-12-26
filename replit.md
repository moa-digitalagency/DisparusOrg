# DISPARUS.ORG - Missing Persons Platform

## Overview
A humanitarian citizen platform for reporting and searching for missing persons in Africa. Features multilingual support (French/English), offline-first PWA capabilities, and moderation tools for content verification.

## Tech Stack
- **Backend**: Python Flask with SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: HTML/Jinja2 + Tailwind CSS (CDN) + JavaScript
- **Maps**: Leaflet with OpenStreetMap
- **i18n**: Flask-Babel for French/English (cookie-based)

## Project Structure
```
app.py                # Flask app with models and routes
main.py               # Entry point
templates/
  base.html           # Base template with header/footer
  index.html          # Landing page with hero, map, stats
  search.html         # Search/filter page
  report.html         # 14+ field report form
  detail.html         # Person detail with contributions
  moderation.html     # Moderation dashboard
  admin.html          # Admin dashboard with stats
static/
  sw.js               # Service worker for offline PWA
  favicon.png         # App icon
  uploads/            # User-uploaded photos
```

## Database Schema
- **disparus_flask**: Missing persons with location, description, contacts
- **contributions_flask**: Sightings and updates from citizens
- **moderation_reports_flask**: Flagged content for review

## Routes
- `GET /` - Landing page with stats, map, recent cases
- `GET /recherche` - Search/filter missing persons
- `GET/POST /signaler` - Report form
- `GET /disparu/<id>` - Person detail page
- `POST /disparu/<id>/contribute` - Add contribution
- `POST /disparu/<id>/report` - Report content
- `GET /set-locale/<locale>` - Change language
- `GET /api/disparus` - JSON API for missing persons
- `GET /api/stats` - Platform statistics
- `GET /manifest.json` - PWA manifest
- `GET /sw.js` - Service worker

## Key Features
1. **Multi-section Report Form**: Identity, Location, Description, Contact
2. **Interactive Maps**: Click to set location, geolocation support
3. **Moderation System**: Flag false/inappropriate content
4. **Multilingual**: French and English with cookie-based preference
5. **Offline-First**: PWA manifest, service worker with caching
6. **Responsive**: Mobile-first design with Tailwind CSS

## Running the Project
```bash
python main.py        # Start Flask development server
```

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-provisioned)
- `SESSION_SECRET` - Session encryption key

## Recent Changes
- 2025-12-26: Complete rebuild with Python Flask/SQLAlchemy (removed all Node.js/React)
- 2025-12-26: Added 50+ African countries with cities dynamic selection
- 2025-12-26: Full 14+ field report form per specifications
- 2025-12-26: Moderation dashboard (/moderation) and Admin dashboard (/admin)
- 2025-12-26: PWA support with service worker and manifest.json
