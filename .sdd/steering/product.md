# Product Overview

**The Sonic Immersive** - A modern digital music store platform that transforms music discovery into an immersive, high-end e-commerce experience

## Core Capabilities

- **Music Catalog Management**: Browse music organized by artists, albums, genres, and songs with rich metadata
- **User Playlists**: Create, manage, and share user-curated playlists
- **Rating & Review System**: Rate and review songs with user-generated content
- **E-commerce**: Purchase tracks with streaming preview functionality
- **Personalized Recommendations**: Recommendation engine based on user behavior and ratings

## Target Use Cases

- **Music Discovery**: Users explore and discover new music through genre filters, recommendations, and curated playlists
- **Collection Building**: Users build their personal music library through purchases and playlist creation
- **Community Engagement**: Users share reviews and ratings to help others discover quality music
- **Streaming Preview**: Users sample tracks before purchase through integrated audio preview

## Value Proposition

**"The Neon Pulse"** - A music store that transcends transactional e-commerce by treating the interface as a living digital venue. The platform combines:
- High-end, immersive visual experience with "Neon Groove" design system
- Complex relational database supporting artists, albums, songs, playlists, and reviews
- Modern, accessible shopping experience targeting intermediate-level e-commerce patterns

## Business Context

- **Difficulty**: Intermediate
- **Scale**: Medium (5-table database with complex relationships)
- **Database**: PostgreSQL on Neon (serverless PostgreSQL)

## Data Model

### Core Entities
- **Artists**: Music artists with country metadata
- **Albums**: Albums linked to artists (one-to-many)
- **Songs**: Individual tracks linked to albums (one-to-many)
- **Playlists**: User-created collections
- **Reviews**: User ratings and reviews for songs

### Key Relationships
```
Artist → Albums → Songs
User → Playlists
User → Reviews → Songs
```

### Database Timestamps
All entities include `created_at` and `updated_at` (TIMESTAMPTZ) for audit trails and temporal queries

### Schema Location
Complete schema definition: `/src/digital-music-store.sql`

---
_Focus on patterns and purpose, not exhaustive feature lists_
