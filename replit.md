# DISPARUS.ORG - Missing Persons Platform

## Overview
A humanitarian citizen platform for reporting and searching for missing persons in Africa. Features multilingual support (French/English), offline-first PWA capabilities, and moderation tools for content verification.

## Tech Stack
- **Backend**: Python Flask with SQLAlchemy
- **Database**: PostgreSQL
- **Frontend**: HTML/Jinja2 + Tailwind CSS (CDN) + JavaScript
- **Maps**: Leaflet with OpenStreetMap
- **i18n**: Flask-Babel for French/English

## Project Structure
```
app/
  __init__.py         # Flask app factory
  models.py           # SQLAlchemy models
  routes.py           # All routes and API endpoints
templates/
  base.html           # Base template with header/footer
  index.html          # Landing page
  search.html         # Search page
  report.html         # Report form
  detail.html         # Person detail page
static/
  sw.js               # Service worker for offline
  favicon.png         # App icon
main.py               # Entry point
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
- 2025-12-26: Rebuilt with Python Flask/SQLAlchemy backend per user request
- 2025-12-26: Added moderation dashboard (/moderation) for reviewing flagged content
- 2025-12-26: Fixed service worker MIME type and DATABASE_URL validation
