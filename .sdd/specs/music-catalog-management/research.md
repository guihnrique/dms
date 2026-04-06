# Research & Design Decisions

## Summary
- **Feature**: `music-catalog-management`
- **Discovery Scope**: New Feature (Greenfield Catalog CRUD System)
- **Key Findings**:
  - SQLAlchemy 2.0 async ORM supports FastAPI async/await pattern seamlessly
  - Soft delete pattern requires deleted_at column + index for performance
  - ISO 3166-1 alpha-2 country codes validated via external library (pycountry)
  - Pagination with cursor-based approach scales better than offset for large datasets
  - Foreign key constraints enforce referential integrity at database level

## Research Log

### SQLAlchemy 2.0 Async ORM Pattern
- **Context**: Need async database operations to align with FastAPI async routes
- **Sources Consulted**:
  - SQLAlchemy 2.0 documentation (async support, relationship loading)
  - FastAPI + SQLAlchemy integration patterns
  - Async session management best practices
- **Findings**:
  - SQLAlchemy 2.0 provides `AsyncSession` for async database operations
  - `selectinload()` for eager loading relationships (prevents N+1 queries)
  - `async with session.begin()` for transaction management
  - AsyncEngine with connection pooling (10-20 connections recommended)
  - Relationship loading strategies: `lazy="selectin"` for async-safe eager loading
- **Implications**:
  - All repository methods use `async def` with `AsyncSession`
  - Relationships use `selectinload()` for efficient loading
  - Database connection via AsyncEngine with pool configuration

### Soft Delete Implementation
- **Context**: Requirement 4.12 specifies soft delete for songs (audit trail)
- **Sources Consulted**:
  - Soft delete patterns in SQLAlchemy
  - Performance implications of filtering deleted records
  - Database indexing strategies for deleted_at columns
- **Findings**:
  - Soft delete pattern: Add `deleted_at TIMESTAMPTZ NULL` column
  - Queries require `WHERE deleted_at IS NULL` filter on all selects
  - Index on `deleted_at` improves filtering performance
  - Partial index: `CREATE INDEX idx_songs_active ON songs(id) WHERE deleted_at IS NULL`
  - SQLAlchemy hybrid property: `@hybrid_property is_deleted`
  - Global query filter: `query.filter(Model.deleted_at.is_(None))`
- **Implications**:
  - Add `deleted_at` column to songs table
  - Repository methods filter out deleted records by default
  - Admin endpoints support `include_deleted=True` query parameter
  - Restore functionality: Set `deleted_at = NULL`

### ISO 3166-1 Country Code Validation
- **Context**: Requirement 1.2 validates country codes for artist records
- **Sources Consulted**:
  - ISO 3166-1 alpha-2 standard (2-letter country codes)
  - pycountry library (Python country code validation)
  - Hardcoded list vs external library trade-offs
- **Findings**:
  - ISO 3166-1 alpha-2: 249 official country codes (e.g., "US", "BR", "JP")
  - `pycountry` library provides official ISO country data
  - Validation: `pycountry.countries.get(alpha_2=code)` returns country or None
  - Library updates when new countries added (Kosovo, South Sudan)
  - Alternative: Hardcoded list in Enum (but requires manual updates)
- **Implications**:
  - Use `pycountry` library for country validation
  - Pydantic validator: `@validator('country')` checks against pycountry
  - Returns 400 Bad Request if invalid country code

### Pagination Strategy: Offset vs Cursor
- **Context**: Requirements specify pagination with page/page_size parameters
- **Sources Consulted**:
  - Pagination patterns for REST APIs
  - Offset-based vs cursor-based pagination performance
  - FastAPI pagination best practices
- **Findings**:
  - **Offset-based**: `LIMIT 20 OFFSET 40` (simple, supports page numbers)
  - **Cursor-based**: `WHERE id > last_id LIMIT 20` (faster for large datasets, no page numbers)
  - Offset performance degrades with high page numbers (database scans all skipped rows)
  - Cursor-based scales linearly (O(1) regardless of position)
  - Requirements specify page/page_size → use offset-based for MVP
  - Cursor-based optimization for future if catalog exceeds 100k records
- **Implications**:
  - Implement offset-based pagination for MVP (page, page_size parameters)
  - Default page_size: 20, max page_size: 100
  - Response includes: items, total, page, page_size, total_pages
  - Monitor query performance; migrate to cursor if degradation observed

### Foreign Key Constraints and Cascade Rules
- **Context**: Requirements specify referential integrity (Requirement 12)
- **Sources Consulted**:
  - PostgreSQL foreign key constraints (ON DELETE CASCADE/RESTRICT)
  - SQLAlchemy relationship cascade configuration
  - Data integrity best practices
- **Findings**:
  - **ON DELETE CASCADE**: When parent deleted, children auto-deleted (albums → songs)
  - **ON DELETE RESTRICT**: Prevent parent deletion if children exist (artists → albums)
  - **ON DELETE SET NULL**: Set foreign key to NULL on parent deletion (not applicable here)
  - SQLAlchemy cascade: `cascade="all, delete-orphan"` for ORM-level cascade
  - Database-level cascade more reliable than ORM-level (works even without app)
- **Implications**:
  - `albums` → `songs`: ON DELETE CASCADE (deleting album deletes songs)
  - `artists` → `albums`: ON DELETE RESTRICT (prevent artist deletion if albums exist)
  - SQLAlchemy relationships match database constraints

### Album Cover Image Handling
- **Context**: Requirement 3.13 supports album cover URLs with validation
- **Sources Consulted**:
  - Image URL validation patterns
  - HTTP HEAD request validation vs regex
  - Default placeholder image strategies
- **Findings**:
  - **Validation approaches**:
    1. Regex: Fast but doesn't verify image exists/reachable
    2. HTTP HEAD request: Verifies existence but slow (network latency)
    3. Background validation: Queue URL checks asynchronously
  - MVP approach: Regex validation only (performance)
  - Fallback: Use default placeholder if URL invalid/unreachable on frontend
  - URL format: `https://example.com/image.jpg` (http/https, common extensions)
- **Implications**:
  - Pydantic validator: Regex for URL format (http/https scheme)
  - No synchronous HEAD requests (blocks API response)
  - Frontend displays placeholder if image fails to load
  - Future: Background job validates URLs and marks invalid ones

### Search Performance Optimization
- **Context**: Requirement 3.11 specifies <200ms search for 10k artists
- **Sources Consulted**:
  - PostgreSQL full-text search (tsvector, tsquery)
  - ILIKE vs full-text search performance
  - GIN index for text search
- **Findings**:
  - **ILIKE pattern matching**: `WHERE name ILIKE '%query%'` (simple, slow for large datasets)
  - **Full-text search**: `tsvector` + `GIN` index (faster, supports ranking)
  - `ILIKE` performance: O(n) scan without index, O(log n) with trigram GIN index
  - Trigram extension: `CREATE EXTENSION pg_trgm` enables GIN index on text columns
  - Index: `CREATE INDEX idx_artists_name_trgm ON artists USING GIN (name gin_trgm_ops)`
  - Query: `WHERE name ILIKE '%query%'` uses trigram index automatically
- **Implications**:
  - Use ILIKE with trigram GIN index for MVP (simpler than full-text)
  - Enable `pg_trgm` extension in database setup
  - Create GIN indexes on artists.name, albums.title, songs.title
  - Monitor search latency; migrate to full-text if needed

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **Repository Pattern (Selected)** | Data access abstraction layer separating business logic from database | Testable, swappable storage, clear boundaries | Extra abstraction layer | Aligns with Clean Architecture in steering |
| Active Record | Model classes include database logic | Simple, less boilerplate | Tight coupling, hard to test | Not recommended for complex domains |
| Query Service | Separate read/write models (CQRS-lite) | Optimized queries, clear intent | More complex, overkill for CRUD | Future consideration if read/write patterns diverge |

**Selected**: Repository Pattern
- Testable: Mock repository in unit tests, real DB in integration tests
- Separation of concerns: Service layer calls repository, doesn't know SQL
- Follows steering Clean Architecture principles
- Enables future storage backend changes (e.g., caching layer)

## Design Decisions

### Decision: Soft Delete for Songs Only (Not Artists/Albums)
- **Context**: Requirement 4.12 specifies soft delete for songs
- **Alternatives Considered**:
  1. **Soft delete all entities** (artists, albums, songs) - Consistent but complex
  2. **Soft delete songs only** - Meets requirements, simpler
  3. **Hard delete all entities** - Simple but loses audit trail
- **Selected Approach**: Soft delete songs only, hard delete artists/albums
  - Songs: `deleted_at TIMESTAMPTZ NULL` column
  - Artists/Albums: Regular DELETE (protected by foreign key constraints)
- **Rationale**:
  - Requirements specify soft delete for songs only (audit trail)
  - Artists/albums protected by ON DELETE RESTRICT (can't delete if albums/songs exist)
  - Simpler implementation than soft delete across all entities
- **Trade-offs**:
  - **Benefit**: Simpler logic, meets requirements exactly
  - **Compromise**: Inconsistent delete behavior across entities
- **Follow-up**: Document soft delete behavior in API documentation

### Decision: Pagination Offset-Based (MVP) with Cursor Migration Path
- **Context**: Need pagination for catalog listings (20 items per page)
- **Alternatives Considered**:
  1. **Offset-based** (page/page_size) - Simple, page numbers
  2. **Cursor-based** (after_id/limit) - Scalable, no page numbers
  3. **Hybrid** (support both) - Flexible but complex
- **Selected Approach**: Offset-based for MVP, document cursor migration
  - Query: `LIMIT page_size OFFSET (page-1)*page_size`
  - Response: `{items, total, page, page_size, total_pages}`
- **Rationale**:
  - Requirements use page/page_size terminology
  - MVP catalog size <100k records (offset performance acceptable)
  - Frontend prefers page numbers for navigation UI
- **Trade-offs**:
  - **Benefit**: Simple implementation, matches requirements
  - **Compromise**: Performance degrades with high page numbers (future issue)
- **Follow-up**: Monitor query latency, migrate to cursor if >100ms p95

### Decision: Trigram GIN Index for Search (Not Full-Text Search)
- **Context**: Requirement 3.11 requires case-insensitive partial match search
- **Alternatives Considered**:
  1. **ILIKE without index** - Simple but slow
  2. **Trigram GIN index** - Fast for ILIKE, moderate complexity
  3. **Full-text search (tsvector)** - Fastest for large text, high complexity
- **Selected Approach**: ILIKE with trigram GIN index
  - Enable `pg_trgm` extension
  - Create GIN index: `CREATE INDEX idx_artists_name_trgm ON artists USING GIN (name gin_trgm_ops)`
  - Query: `WHERE name ILIKE '%query%'` (index used automatically)
- **Rationale**:
  - Partial match requirement (ILIKE supports `%query%`)
  - Trigram index accelerates ILIKE without query rewrite
  - Simpler than full-text search (no tsvector columns, no ts_rank)
- **Trade-offs**:
  - **Benefit**: Fast search (<200ms), simple queries
  - **Compromise**: Not as fast as full-text for very large catalogs
- **Follow-up**: Benchmark search latency at 10k, 50k, 100k records

### Decision: Foreign Key Constraints with Cascade/Restrict
- **Context**: Requirement 12 specifies referential integrity enforcement
- **Alternatives Considered**:
  1. **Database-level constraints** - Strong guarantee, automatic enforcement
  2. **Application-level checks** - Flexible but error-prone
  3. **No constraints** - Fast but data integrity risk
- **Selected Approach**: Database-level foreign keys with cascade rules
  - `albums.artist_id` → `artists.id` ON DELETE RESTRICT
  - `songs.album_id` → `albums.id` ON DELETE CASCADE
- **Rationale**:
  - Database constraints enforced even if application bypassed
  - ON DELETE RESTRICT prevents orphaned albums
  - ON DELETE CASCADE cleans up songs automatically when album deleted
- **Trade-offs**:
  - **Benefit**: Strong data integrity guarantee
  - **Compromise**: Cannot delete artist if albums exist (intentional protection)
- **Follow-up**: Integration tests verify cascade/restrict behavior

### Decision: Album Cover URL Validation (Regex Only for MVP)
- **Context**: Requirement 3.13 validates album cover URLs
- **Alternatives Considered**:
  1. **Regex validation** - Fast but doesn't verify reachability
  2. **HTTP HEAD request** - Verifies existence but slow (500ms+)
  3. **Background validation** - Queue URL checks, async update
- **Selected Approach**: Regex validation for MVP
  - Regex: `^https?://.*\.(jpg|jpeg|png|gif|webp)$`
  - Frontend fallback: Display placeholder if image fails to load
- **Rationale**:
  - Synchronous HEAD requests block API response (poor UX)
  - Regex validates format (http/https, common extensions)
  - Frontend can handle broken images gracefully
- **Trade-offs**:
  - **Benefit**: Fast API response, no external dependencies
  - **Compromise**: Doesn't verify image exists/reachable
- **Follow-up**: Background job validates URLs (future enhancement)

## Risks & Mitigations

### Risk 1: N+1 Query Problem with Relationships
- **Description**: Loading albums with artist data causes N+1 queries (1 album query + N artist queries)
- **Impact**: Poor performance, slow API responses
- **Mitigation**:
  - Use `selectinload()` for eager loading: `query.options(selectinload(Album.artist))`
  - Relationship configuration: `lazy="selectin"` in SQLAlchemy models
  - Monitor query count in logs (log all SQL queries in dev)
  - Integration tests verify single query per endpoint

### Risk 2: Soft Delete Filter Forgotten in Queries
- **Description**: Developers forget `WHERE deleted_at IS NULL` filter, exposing deleted songs
- **Impact**: Deleted songs appear in API responses
- **Mitigation**:
  - Base repository method `_filter_active()` applies deleted_at filter
  - All query methods call `_filter_active()` by default
  - Admin endpoints explicitly opt-in with `include_deleted=True`
  - Integration tests verify deleted songs not returned

### Risk 3: Pagination Performance Degradation at Scale
- **Description**: Offset pagination slow for high page numbers (e.g., page 1000)
- **Impact**: Slow API responses for deep pagination
- **Mitigation**:
  - Monitor p95 latency for pagination queries
  - Alert if latency exceeds 200ms
  - Document cursor-based pagination migration path
  - Limit max page number to 100 (reject requests for page > 100)

### Risk 4: Invalid Country Codes from External Changes
- **Description**: pycountry library updates may break existing validation
- **Impact**: Previously valid country codes rejected
- **Mitigation**:
  - Pin pycountry library version in requirements.txt
  - Update pycountry as part of controlled upgrade process
  - Test country validation after pycountry updates
  - Fallback: Allow unknown country codes with warning (future)

### Risk 5: Album Cover URL Injection Attack
- **Description**: Malicious URLs in album_cover_url field (e.g., `javascript:` scheme)
- **Impact**: XSS vulnerability if URL rendered without sanitization
- **Mitigation**:
  - Regex validation restricts schemes to http/https only
  - Frontend sanitizes URLs before rendering in `<img src>`
  - Content Security Policy (CSP) blocks non-http schemes
  - Pydantic validator rejects non-http/https URLs

## References

### Official Documentation
- [SQLAlchemy 2.0 Async](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html) - Async ORM patterns
- [FastAPI + SQLAlchemy](https://fastapi.tiangolo.com/tutorial/sql-databases/) - Integration guide
- [PostgreSQL Indexes](https://www.postgresql.org/docs/current/indexes.html) - GIN, trigram
- [pycountry](https://pypi.org/project/pycountry/) - ISO country codes

### Design Patterns
- Repository Pattern - Data access abstraction
- Soft Delete Pattern - Audit trail without data loss

### Internal References
- `.sdd/steering/structure.md` - Database schema (artists, albums, songs tables)
- `.sdd/steering/tech.md` - SQLAlchemy ORM, FastAPI async patterns
- `src/digital-music-store.sql` - Database schema definition
