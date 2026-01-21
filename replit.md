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
app.py                # Flask app factory
config.py             # Configuration classes
main.py               # Entry point

routes/               # Flask Blueprints
  __init__.py         # Blueprint registration
  public.py           # /, /recherche, /signaler, /disparu/:id
  admin.py            # /admin/*
  api.py              # /api/* JSON endpoints

models/               # SQLAlchemy models
  __init__.py         # db instance
  disparu.py          # Missing person model
  contribution.py     # Contribution/sighting model
  user.py             # User and ModerationReport models

utils/                # Utility functions
  geo.py              # Countries/cities data, geolocation
  pdf_gen.py          # PDF/QR code generation
  search.py           # Search indexing

services/             # Business logic
  signalement.py      # Report creation/management
  notifications.py    # Email/SMS notifications
  analytics.py        # Platform statistics

security/             # Authentication
  auth.py             # Login decorators
  rate_limit.py       # Rate limiting

algorithms/           # AI/Analysis
  clustering.py       # Geographic hotspots
  matching.py         # Photo matching

lang/                 # Translation files
  fr.json             # French translations
  en.json             # English translations

statics/              # Static assets (unique folder)
  css/                # Stylesheets
  js/                 # JavaScript (includes sw.js)
  img/                # Images/icons (includes favicon.png)
  uploads/            # User uploads

templates/            # Jinja2 templates
  base.html           # Base template
  index.html          # Landing page
  search.html         # Search page
  report.html         # Report form
  detail.html         # Person detail
  moderation.html     # Moderation dashboard
  admin.html          # Admin dashboard
```

## Database Schema
- **disparus_flask**: Missing persons with location, description, contacts
- **contributions_flask**: Sightings and updates from citizens (with is_approved validation)
- **moderation_reports_flask**: Flagged content for review
- **users_flask**: User accounts with role-based access
- **roles_flask**: Role definitions with permissions and menu access
- **activity_logs_flask**: Activity logging for all user actions
- **downloads_flask**: Download tracking for PDFs, images, exports
- **site_settings_flask**: Platform configuration (SEO, security, general)

## Routes
### Public Blueprint (routes/public.py)
- `GET /` - Landing page with stats, map, recent cases
- `GET /recherche` - Search/filter missing persons
- `GET/POST /signaler` - Report form
- `GET /disparu/<id>` - Person detail page
- `POST /disparu/<id>/contribute` - Add contribution
- `POST /disparu/<id>/report` - Report content
- `GET /set-locale/<locale>` - Change language

### Admin Blueprint (routes/admin.py)
- `GET /admin/login` - Admin login page
- `GET /admin/logout` - Logout
- `GET /admin/` - Admin dashboard with sidebar
- `GET /admin/reports` - All reports with pagination/filters
- `GET /admin/moderation` - Moderation dashboard
- `GET /admin/contributions` - All contributions with approve/reject
- `GET /admin/statistics` - Platform statistics
- `GET /admin/map` - Interactive map view
- `GET /admin/users` - User management (CRUD)
- `GET /admin/roles` - Role management with permissions
- `GET /admin/logs` - Activity logs with filters
- `GET /admin/downloads` - Download tracking
- `GET /admin/settings` - SEO, security, general settings
- `POST /admin/contributions/<id>/approve` - Approve contribution
- `POST /admin/contributions/<id>/reject` - Reject contribution
- `POST /admin/moderation/<id>/resolve` - Resolve report
- `POST /admin/disparu/<id>/status` - Update status
- `POST /admin/disparu/<id>/delete` - Delete record

### API Blueprint (routes/api.py)
- `GET /api/disparus` - JSON list of missing persons (supports lat/lng for proximity sorting)
- `GET /api/disparus/nearby` - Get nearby disparus sorted by distance (requires lat/lng params)
- `GET /api/disparus/<id>` - Single person with contributions
- `GET /api/stats` - Platform statistics
- `GET /api/countries` - List of countries
- `GET /api/cities/<country>` - Cities for country
- `GET /api/search` - Search API

### Utility Routes
- `GET /manifest.json` - PWA manifest
- `GET /sw.js` - Service worker
- `GET /moderation` - Moderation page

## Key Features
1. **Multi-section Report Form**: Identity, Location, Description, Contact
2. **Interactive Maps**: Click to set location, geolocation support, hover previews
3. **Moderation System**: Flag false/inappropriate content
4. **Multilingual**: French and English with cookie-based preference
5. **Offline-First**: PWA manifest, service worker with caching
6. **Responsive**: Mobile-first design with Tailwind CSS
7. **50+ African Countries**: Comprehensive city lists
8. **Role-Based Access Control**: 4 system roles (admin, moderator, ngo, secours)
9. **Activity Logging**: Track all actions, IP addresses, security events
10. **Download Tracking**: Monitor PDF/image downloads
11. **Contribution Validation**: Approve/reject workflow for contributions
12. **SEO Configuration**: Meta tags, OpenGraph, Google Analytics/GTM
13. **Custom Script Injection**: Head/body scripts for tracking
14. **Geolocation-Based Sorting**: Reports sorted by proximity to user's detected location
15. **Country Filter**: Persistent dropdown filter on homepage and admin map (localStorage)
16. **Placeholder Images**: Configurable male/female placeholders for PDF/image exports when no photo available

## User Roles
- **admin**: Full access to all features
- **moderator**: Content moderation, contribution validation
- **ngo**: Reports, statistics, exports
- **secours**: Reports, map access

## Running the Project
```bash
python main.py        # Start Flask development server
python init_db.py     # Initialize database tables and default data
```

## Database Initialization
The `init_db.py` script handles:
1. Creating all database tables
2. Initializing default roles (admin, moderator, ngo, secours)
3. Initializing default site settings (SEO, footer, security)
4. Creating admin user if ADMIN_PASSWORD is set

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-provisioned)
- `SESSION_SECRET` - Session encryption key
- `ADMIN_USERNAME` - Admin username for login
- `ADMIN_PASSWORD` - Admin password for login

## Recent Changes
- 2026-01-21: Added admin Data page for export, backup, restore, and delete operations
- 2026-01-21: Export data to JSON/CSV (all countries or specific country)
- 2026-01-21: Backup/restore database with full data preservation
- 2026-01-21: Delete data by country with confirmation
- 2026-01-21: Reduced logo size in header when custom logo is set
- 2026-01-21: Added geolocation-based map zoom to user's detected city/location
- 2026-01-21: Reports sorted by proximity (closest first) using Haversine formula
- 2026-01-21: Added country filter dropdown on homepage and admin map with localStorage persistence
- 2026-01-21: Added /api/disparus/nearby endpoint for proximity-sorted results
- 2026-01-04: Added PDF, social media image, and QR code download routes
- 2026-01-04: Enhanced detail page map with all contribution locations and custom markers
- 2026-01-04: Admin authentication uses ADMIN_USERNAME and ADMIN_PASSWORD env vars
- 2026-01-04: Enhanced security - CSRF protection, rate limiting on API
- 2026-01-04: Added init_db.py for database initialization
- 2026-01-04: Logo and favicon now configurable via admin settings
- 2026-01-04: Added file upload validation (allowed extensions/mimetypes)
- 2025-12-29: Added user management with CRUD, role assignment
- 2025-12-29: Added role management with permissions and menu access control
- 2025-12-29: Added activity logging system with severity levels and security events
- 2025-12-29: Added download tracking for all file downloads
- 2025-12-29: Enhanced settings with SEO (meta tags, GA, GTM, OpenGraph), security, custom scripts
- 2025-12-29: Added contribution validation workflow (approve/reject)
- 2025-12-29: Admin sidebar now has 3 sections: Main menu, Management, System
- 2025-12-29: Admin panel redesigned with left sidebar navigation menu
- 2025-12-29: Added admin pages: reports, contributions, statistics, map, settings
- 2025-12-29: Admin authentication with login/logout and session-based security
- 2025-12-26: Restructured to modular architecture with routes/, models/, services/, utils/, security/, algorithms/
- 2025-12-26: Flask Blueprints for public, admin, and API routes
- 2025-12-26: Added PDF/QR generation, clustering algorithms, photo matching stubs
- 2025-12-26: Security module with auth decorators and rate limiting
- 2025-12-26: Renamed static/ to statics/ per user request
- 2026-01-04: Enhanced PDF generator with premium design (colors, branding, QR codes)
- 2026-01-04: Created comprehensive documentation in docs/ folder

## Documentation

Complete documentation is available in the `docs/` folder:

- **README.md** - Documentation index
- **ARCHITECTURE.md** - Technical architecture, database schema, data flows
- **INSTALLATION.md** - Installation and deployment guide
- **API.md** - API reference with endpoints and examples
- **GUIDE_UTILISATEUR.md** - User guide (French)
- **GUIDE_ADMIN.md** - Administrator guide (French)
- **PRESENTATION.md** - Project presentation, vision, mission
- **PARTENARIATS.md** - Partnership opportunities
