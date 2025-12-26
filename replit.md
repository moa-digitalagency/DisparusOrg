# DISPARUS.ORG - Missing Persons Platform

## Overview
A humanitarian citizen platform for reporting and searching for missing persons in Africa. Features multilingual support (French/English), offline-first PWA capabilities, and moderation tools for content verification.

## Tech Stack
- **Frontend**: React + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: Node.js + Express
- **Database**: PostgreSQL with Drizzle ORM
- **Maps**: Leaflet with OpenStreetMap
- **State**: TanStack Query + Zustand
- **i18n**: Custom Zustand-based translation system

## Project Structure
```
client/
  src/
    components/       # Reusable UI components
      Header.tsx      # Navigation header with search
      Footer.tsx      # Site footer with links
      LeafletMap.tsx  # OpenStreetMap integration
      MissingPersonCard.tsx  # Card for displaying missing persons
      Timeline.tsx    # Contribution history timeline
      ModerationDialog.tsx   # Content flagging dialog
      FilterBar.tsx   # Search filters
      StatsDisplay.tsx # Statistics display
      OfflineIndicator.tsx   # PWA offline status
    pages/
      Landing.tsx     # Homepage with stats, map, recent cases
      Search.tsx      # Search/filter missing persons
      ReportForm.tsx  # Multi-step report form
      DisparuDetail.tsx # Individual case detail page
    lib/
      i18n.ts         # Internationalization (FR/EN)
      theme.tsx       # Dark/light theme provider
      queryClient.ts  # TanStack Query setup
    hooks/
      use-toast.ts    # Toast notifications
  public/
    manifest.json     # PWA manifest
    favicon.png
server/
  db.ts              # PostgreSQL connection
  storage.ts         # Database operations
  routes.ts          # API endpoints
shared/
  schema.ts          # Drizzle models + Zod schemas
```

## Database Schema
- **disparus**: Missing persons with location, description, contacts
- **contributions**: Sightings and updates from citizens
- **moderation_reports**: Flagged content for review
- **users**: Basic user accounts (for future admin)

## API Endpoints
- `GET /api/disparus` - List missing persons with filters
- `GET /api/disparus/:id` - Get single person by public ID
- `POST /api/disparus` - Create new report
- `PATCH /api/disparus/:id` - Update report
- `GET /api/contributions/:id` - Get contributions for a person
- `POST /api/contributions` - Add contribution
- `POST /api/moderation` - Report content
- `GET /api/stats` - Get platform statistics

## Key Features
1. **Multi-step Report Form**: Identity → Location → Description → Contact
2. **Interactive Maps**: Click to set location, geolocation support
3. **Moderation System**: Flag false/inappropriate content
4. **Multilingual**: French and English with locale detection
5. **Offline-First**: PWA manifest, service worker ready
6. **Responsive**: Mobile-first design

## Running the Project
```bash
npm run dev        # Start development server
npm run db:push    # Push schema changes to database
```

## Environment Variables
- `DATABASE_URL` - PostgreSQL connection string (auto-provisioned)
- `SESSION_SECRET` - Session encryption key

## Recent Changes
- 2025-12-26: Initial MVP with full CRUD, i18n, PWA support, and moderation
