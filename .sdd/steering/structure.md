# Project Structure

## Organization Philosophy

**Prototype-First Design**: Visual mockups organized by screen/component to establish design system before backend implementation

## Directory Patterns

### Database Schema (`/src/`)
**Purpose**: PostgreSQL schema for Neon deployment
- `digital-music-store.sql` - Complete database schema with 5 tables

**Schema Structure:**
```sql
artists (id, name, country, timestamps)
  ↓
albums (id, artist_id, title, release_year, timestamps)
  ↓
songs (id, album_id, title, duration_seconds, timestamps)
  
playlists (id, title, owner_user_id, timestamps)
reviews (id, user_id, song_id, rating, body, timestamps)
```

### Stitch Mockups (`/src/stitch/`)
**Purpose**: HTML/CSS prototypes demonstrating visual design and user flows  
**Structure**: Screen-based organization with supporting assets
```
src/stitch/
├── project_brief_digital_music_store.html  # Project specification
└── stitch/
    ├── neon_groove/DESIGN.md               # Design system documentation
    ├── explore_home/                       # Homepage/browse view
    ├── album_detail/                       # Album detail screen
    ├── artist_profile/                     # Artist profile screen
    └── my_library/                         # User library view
```

**Pattern**: Each screen directory contains:
- `code.html` - Full page prototype
- `screen.png` - Visual reference/screenshot

### SDD System (`.sdd/`)
**Purpose**: Spec-Driven Development metadata and project memory  
**Pattern**: 
- `.sdd/steering/` - Project-wide patterns and context
- `.sdd/specs/` - Feature specifications and implementations
- `.sdd/settings/` - Templates and rules (not documented in steering)

## Naming Conventions

### Files
- **HTML Prototypes**: `code.html` (standard for Stitch exports)
- **Design Docs**: `DESIGN.md`, `CLAUDE.md` (uppercase for prominence)
- **Screenshots**: `screen.png` (descriptive naming)

### Directories
- **Screens**: `snake_case` (e.g., `explore_home`, `artist_profile`)
- **System dirs**: Lowercase with dashes where needed (`.sdd`)

## Design System Organization

### "Neon Groove" System (`neon_groove/DESIGN.md`)
Central design system document defining:
- Color palette and surface hierarchy
- Typography scale (Space Grotesk + Manrope)
- Component primitives (buttons, cards, inputs)
- Layout principles (glassmorphism, tonal layering)

### Screen Categories
**Browse/Discovery**:
- `explore_home` - Main browsing interface with genre filters, recommendations

**Content Details**:
- `album_detail` - Album view with track listings
- `artist_profile` - Artist biography and discography

**User Features**:
- `my_library` - Personal collection management

## Tailwind Configuration Pattern

Screens use inline `<script>` configuration for Tailwind theme:
```javascript
tailwind.config = {
  darkMode: "class",
  theme: {
    extend: {
      colors: { /* custom design tokens */ },
      fontFamily: { /* Space Grotesk, Manrope */ },
      borderRadius: { /* custom radii */ }
    }
  }
}
```

## Code Organization Principles

**1. Component-Centric HTML**
- Semantic section elements (`<aside>`, `<main>`, `<footer>`)
- BEM-inspired class naming for custom styles
- Utility-first Tailwind for layout/styling

**2. Design Token Consistency**
- Custom Tailwind colors match design system exactly
- Spacing/sizing use consistent scale
- Typography uses defined font families

**3. Mobile-First Responsive**
- Base styles for mobile
- `md:` prefix for tablet/desktop breakpoints
- Hidden/visible utility classes for layout shifts

**4. Asset Organization**
- External images via Google Content API (placeholder CDN)
- Inline SVG patterns discouraged (use Material Symbols)

## Implementation Structure (React + Python)

Expected monorepo or separated structure:

### Backend (Python)
```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI/Flask app entry
│   ├── config.py            # Environment config (DATABASE_URL, JWT_SECRET)
│   ├── models/              # SQLAlchemy models
│   │   ├── artist.py
│   │   ├── album.py
│   │   ├── song.py
│   │   ├── playlist.py
│   │   └── review.py
│   ├── routers/             # API endpoints
│   │   ├── artists.py
│   │   ├── albums.py
│   │   ├── songs.py
│   │   ├── playlists.py
│   │   └── reviews.py
│   ├── schemas/             # Pydantic schemas (request/response)
│   ├── services/            # Business logic
│   └── database.py          # Database connection
├── requirements.txt         # Python dependencies
└── .env.example             # Template for environment variables
```

### Frontend (React)
```
frontend/
├── public/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── ui/              # Design system primitives (Button, Card, Input)
│   │   ├── layout/          # Layout components (Sidebar, Player)
│   │   └── features/        # Feature-specific components
│   ├── pages/               # Screen implementations from mockups
│   │   ├── Explore.jsx      # explore_home mockup
│   │   ├── AlbumDetail.jsx  # album_detail mockup
│   │   ├── ArtistProfile.jsx
│   │   └── MyLibrary.jsx
│   ├── hooks/               # Custom React hooks
│   ├── services/            # API client (axios/fetch)
│   ├── context/             # React Context for state
│   ├── utils/               # Helper functions
│   ├── styles/              # Tailwind config, global styles
│   │   └── tailwind.config.js  # Neon Groove theme
│   └── App.jsx              # Root component
├── package.json
└── .env.example
```

### Root Level
```
/
├── backend/                 # Python API
├── frontend/                # React app
├── src/
│   ├── digital-music-store.sql  # Database schema
│   └── stitch/              # Design mockups (reference)
├── .gitignore               # MUST include .env, __pycache__, node_modules
└── README.md
```

## Import Organization

### React (Frontend)
```jsx
// Absolute imports (configured in jsconfig.json or tsconfig.json)
import { Button } from '@/components/ui/Button'
import { useAuth } from '@/hooks/useAuth'
import { fetchArtists } from '@/services/api'

// Relative imports for co-located files
import styles from './Explore.module.css'
```

### Python (Backend)
```python
# Absolute imports from app root
from app.models.artist import Artist
from app.schemas.artist import ArtistSchema
from app.services.artist_service import ArtistService

# Standard library first, then third-party, then local
import os
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
```

### Environment Variables
**CRITICAL**: Never commit `.env` files
```bash
# Frontend (.env)
VITE_API_URL=http://localhost:8000
VITE_APP_NAME="The Sonic Immersive"

# Backend (.env)
DATABASE_URL=postgresql://user:pass@neon.tech:5432/dbname
JWT_SECRET=<generate-with-openssl-rand-hex-32>
CORS_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---
_Document patterns, not file trees. New files following patterns shouldn't require updates_
