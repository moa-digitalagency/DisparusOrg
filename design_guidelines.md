# Design Guidelines - DISPARUS.ORG Missing Persons Platform

## Design Approach
**Humanitarian Crisis Response Pattern** - Drawing from established emergency/humanitarian platforms (ICRC, Amber Alert, disaster response systems). This platform requires immediate trust, clarity under stress, and universal accessibility. Form follows function with purposeful visual hierarchy.

---

## Core Design Principles

### 1. Clarity Over Decoration
- Information architecture prioritizes scanning and quick comprehension
- Every element serves a functional purpose - no decorative flourishes
- High contrast, large touch targets, clear labeling

### 2. Mobile-First + Offline Resilience  
- Design for 320px minimum width
- Progressive enhancement for desktop
- Clear loading states and offline indicators
- Optimize for intermittent connectivity

### 3. Universal Accessibility
- Multi-literacy design (icons + text)
- WCAG AAA compliance where possible
- Large, readable fonts (never below 16px base)
- Clear form validation with multiple feedback types

---

## Typography System

**Font Stack:** Inter (via Google Fonts CDN) - excellent multilingual support, high legibility

**Hierarchy:**
- Display (Hero stats): text-4xl to text-6xl, font-bold
- Page Titles: text-3xl to text-4xl, font-semibold  
- Section Headers: text-2xl, font-semibold
- Card Titles: text-xl, font-semibold
- Body Text: text-base (16px), font-normal
- Captions/Metadata: text-sm, font-medium
- Form Labels: text-sm, font-semibold, uppercase tracking-wide

**Critical:** Maintain 1.6 line-height for body text (readability under stress)

---

## Layout System

**Spacing Primitives:** Use Tailwind units: 1, 2, 4, 6, 8, 12, 16, 24
- Component internal padding: p-4 to p-6
- Section vertical spacing: py-12 (mobile), py-16 to py-24 (desktop)
- Card gaps: gap-4 to gap-6
- Form field spacing: space-y-6

**Grid System:**
- Mobile: Single column (grid-cols-1)
- Tablet: 2 columns for cards (md:grid-cols-2)
- Desktop: 3 columns max for missing persons grid (lg:grid-cols-3)
- Never exceed 4 columns

**Container Strategy:**
- Full-width map sections: w-full
- Content sections: max-w-7xl mx-auto px-4
- Forms: max-w-2xl mx-auto
- Reading content: max-w-3xl

---

## Component Library

### Header (Fixed Position)
- Logo left, search bar center (expandable on mobile), "Signaler Disparition" CTA button right
- Height: h-16 on mobile, h-20 on desktop
- Search: Prominent with Heroicons magnifying glass
- Sticky: sticky top-0 with backdrop-blur

### Missing Person Cards
**Structure:**
- Photo: aspect-square, object-cover, rounded-lg (NOT rounded-full - need clear facial recognition)
- Border: 2px solid, subtle shadow
- Padding: p-4
- Info stack: Name (font-bold, text-lg), Age/Gender (text-sm), Location (text-sm with map pin icon), ID badge (monospace font)
- CTA: "Voir Détails" button, full-width within card
- Urgent indicator: Top-right corner badge for recent (<48h) cases

**Grid:** gap-6, responsive columns as above

### Forms (Critical UX)
**Layout:**
- Single column always (no multi-column forms)
- Label above input (never side-by-side)
- Required asterisk: Red, inline with label
- Field spacing: space-y-6 between fields, space-y-2 between label and input
- Input heights: h-12 minimum (easy tapping)
- Textareas: min-h-32
- Dropdowns: Custom styled with Heroicons chevron-down

**Field Groups:**
- Related fields wrapped in subtle border (p-6, rounded-lg)
- Repeatable contacts: Each contact in own bordered section with delete icon

**Buttons:**
- Primary CTA: px-8 py-3, rounded-lg, font-semibold, w-full on mobile, w-auto on desktop
- Secondary: Same size, different visual treatment
- Icon buttons: w-10 h-10, rounded-full

### Map Integration (OpenStreetMap)
- Landing page: h-96 minimum for heatmap
- Detail page: h-64 for timeline visualization  
- Form: h-80 for location selection
- Always show zoom controls and geolocation button
- Markers: Custom with photo thumbnails where available

### Timeline (Contribution History)
- Vertical line on left (2px)
- Timeline nodes: Larger circle for major events (person found), smaller for sightings
- Each entry: Card with timestamp, contribution type icon, description, location
- Spacing: space-y-6 between entries

### Stats Display (Hero)
**Layout:** 3-column grid (md:grid-cols-3) within bordered container
- Large number: text-5xl, font-bold
- Label below: text-sm, uppercase
- Icons from Heroicons: user-group, map-pin, clock

### Document Download Section
**Cards for each format:** PDF Public, PDF Admin, Social Media Image
- Icon: Document icon from Heroicons
- Title + file size
- Download button below
- QR code preview (small, 80x80px)

---

## Page-Specific Layouts

### Landing Page
1. **Hero Section:** h-auto (not forced viewport)
   - Stats display (3-column grid)
   - Primary CTA "Signaler une Disparition"
   - Secondary search prompt
   - py-16 to py-20

2. **Interactive Map:** Full-width, h-96, heatmap overlay

3. **Recent Missing Persons:** 
   - Section header with filter chips (Tous, Enfants, Adultes)
   - Grid of cards (responsive columns)
   - "Voir Plus" button centered below

4. **How to Help:** 3-column grid (stacks mobile)
   - Icon above (96x96 size)
   - Heading + description
   - Arrow link

5. **Footer:** 4-column grid (desktop), stacks mobile
   - Countries list (max-h-64, overflow-y-auto)
   - Quick links
   - Contact info  
   - Legal links

### Missing Person Detail Page
**Two-column layout (desktop), stacks mobile:**

**Left Column (md:w-2/5):**
- Photo: Full width, aspect-[3/4], rounded-lg
- ID badge prominent
- Download documents section

**Right Column (md:w-3/5):**
- Essential info (name, age, details) in bordered sections
- Map with last known location
- Contribution timeline (chronological)
- Contribution form at bottom

### Report Form Page
- Centered, max-w-2xl
- Progress indicator at top (Step 1 of 4)
- Form sections with clear headers
- Map selection integrated inline
- Bottom navigation: "Retour" + "Continuer" buttons

---

## Images

**Hero Section:** NO large hero image on landing page - prioritize immediate functionality (search + stats)

**Missing Person Photos:**
- Always aspect-square for consistency in grids
- object-cover to handle varied uploads
- Placeholder: Heroicons user-circle (96x96) when no photo
- Detail page: Larger version, aspect-[3/4], max-w-md

**Social Sharing Generated Images:**
- Created server-side, not shown in UI except as download preview

---

## Icons
**Use Heroicons (Outline style) via CDN** for:
- Navigation: magnifying-glass, bell, user-circle
- Forms: map-pin, calendar, clock, photo, document-text
- Status: check-circle (found), exclamation-triangle (urgent), eye (sighting)
- Actions: arrow-down-tray (download), share, printer
- UI: chevron-down, x-mark, plus

Size: w-5 h-5 for inline, w-6 h-6 for prominent

---

## Responsive Behavior
- Breakpoints: sm:640px, md:768px, lg:1024px, xl:1280px
- Mobile: Stack all multi-column layouts, full-width buttons, expanded touch targets
- Desktop: Multi-column grids, fixed sidebar on detail pages, inline form buttons

---

## Accessibility & Internationalization
- All form labels with `for` attributes
- ARIA labels on icon-only buttons
- Language switcher: Flag icons + language code in header
- RTL support: Use Tailwind's rtl: modifiers for Arabic locales
- Focus states: 2px outline, visible ring

This platform's design success is measured by how quickly stressed users can report/find missing persons, not aesthetic novelty.