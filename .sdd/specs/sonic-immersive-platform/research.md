# Research & Design Decisions

## Summary
- **Feature**: `sonic-immersive-platform`
- **Discovery Scope**: New Feature (Greenfield Full-Stack Platform)
- **Key Findings**:
  - Clean Architecture with Service Layer pattern best suits separation of concerns between FastAPI routes, business logic, and data access
  - Neon PostgreSQL serverless requires connection pooling strategy (pgbouncer or SQLAlchemy pool) for production
  - TDD approach requires pytest fixtures/factories for database testing isolation
  - React 18 with Vite build tool provides optimal developer experience with Fast Refresh and code splitting
  - JWT + bcrypt authentication is industry standard but requires proper token refresh strategy

## Research Log

### FastAPI + SQLAlchemy Architecture Pattern
- **Context**: Need to define backend architecture that scales and maintains testability
- **Sources Consulted**: 
  - FastAPI official documentation (dependency injection patterns)
  - SQLAlchemy 2.0 documentation (async support, ORM patterns)
  - Clean Architecture principles (Uncle Bob)
- **Findings**:
  - **Router → Service → Repository** pattern provides clear separation
  - FastAPI dependency injection ideal for service/repository injection
  - SQLAlchemy 2.0 async support aligns with FastAPI async/await
  - Pydantic schemas separate from SQLAlchemy models prevents ORM leakage
- **Implications**: 
  - Design must define Service layer for business logic
  - Repository pattern for data access abstraction
  - Separate Pydantic schemas for API contracts

### Neon PostgreSQL Connection Strategy
- **Context**: Neon is serverless PostgreSQL - needs connection pooling strategy
- **Sources Consulted**:
  - Neon documentation (connection pooling recommendations)
  - SQLAlchemy connection pool documentation
  - FastAPI + PostgreSQL production patterns
- **Findings**:
  - Neon provides built-in connection pooling via connection string
  - SQLAlchemy AsyncEngine with pool configuration recommended
  - Connection pool sizing: 10-20 connections typical for medium apps
  - Health checks required for connection validation
- **Implications**:
  - Database module must configure AsyncEngine with proper pool settings
  - Environment variable: `DATABASE_URL` with pooling enabled
  - Health check endpoint validates database connectivity

### JWT Authentication & Security
- **Context**: Requirements specify JWT auth with bcrypt password hashing
- **Sources Consulted**:
  - FastAPI security documentation (OAuth2PasswordBearer)
  - python-jose library for JWT handling
  - bcrypt library documentation
- **Findings**:
  - FastAPI OAuth2PasswordBearer provides standard JWT flow
  - python-jose supports HS256 algorithm for JWT signing
  - bcrypt cost factor 12-14 recommended (steering specifies 12 minimum)
  - Token expiration: 24 hours per requirements
  - Refresh token strategy needed for production (out of MVP scope)
- **Implications**:
  - Auth service must handle JWT generation/validation
  - Password hashing service with bcrypt
  - Middleware for JWT validation on protected routes
  - JWT_SECRET environment variable required

### React + Tailwind + TypeScript Setup
- **Context**: Frontend stack defined in steering, need optimal project structure
- **Sources Consulted**:
  - Vite documentation (React + TypeScript template)
  - React 18 documentation (concurrent features, suspense)
  - Tailwind CSS v3 documentation (JIT mode, configuration)
- **Findings**:
  - Vite faster than Create React App (HMR, build performance)
  - React 18 Suspense + Error Boundaries for loading/error states
  - Tailwind JIT mode with custom config for "Neon Groove" design system
  - Feature-based folder structure preferred over layer-based
- **Implications**:
  - Frontend: Vite as build tool
  - Component structure: `/src/features/[feature]/components`
  - Shared UI components: `/src/components/ui/`
  - Tailwind config extends with custom "Neon Groove" tokens

### TDD Testing Strategy
- **Context**: TDD mandatory per steering, need comprehensive test infrastructure
- **Sources Consulted**:
  - pytest documentation (fixtures, async support)
  - pytest-asyncio for async test support
  - factory_boy for test data factories
  - React Testing Library documentation
  - Jest + Vitest comparison
- **Findings**:
  - **Backend**: pytest + pytest-asyncio + pytest-cov + factory_boy
  - **Frontend**: Jest + React Testing Library (mature ecosystem)
  - Vitest emerging alternative (faster, Vite-native) but Jest more stable
  - Database testing: use test database with migrations, rollback per test
  - API testing: httpx.AsyncClient for FastAPI test client
- **Implications**:
  - Backend fixtures for db_session, test_client, authenticated_user
  - Frontend: MSW (Mock Service Worker) for API mocking
  - E2E: Playwright for critical flows
  - Coverage: 80% backend, 70% frontend (per steering)

### Design System "Neon Groove" Implementation
- **Context**: Mockups define glassmorphism design system, needs React implementation
- **Sources Consulted**:
  - Existing Stitch mockups (`/src/stitch/stitch/neon_groove/DESIGN.md`)
  - Tailwind CSS custom configuration
  - CSS backdrop-filter browser support
- **Findings**:
  - Glassmorphism: `backdrop-blur-xl` + `bg-white/5` pattern
  - Custom color tokens via Tailwind extend config
  - Space Grotesk + Manrope fonts via Google Fonts
  - Material Symbols icons via CDN or npm package
  - Minimum border radius: 0.75rem (no 90-degree corners)
- **Implications**:
  - Tailwind config must define all color tokens from mockups
  - Typography: custom font-family classes
  - Shared Button, Card, Input components with design system styles
  - Accessibility: ARIA labels, keyboard navigation, WCAG AA contrast

### Recommendation Algorithm Approach
- **Context**: Requirements specify personalized recommendations based on playlists/reviews
- **Sources Consulted**:
  - Collaborative filtering basics
  - Content-based filtering
  - Hybrid recommendation approaches
- **Findings**:
  - MVP approach: Simple scoring algorithm
    - User's playlist songs → extract genres/artists
    - User's high-rated reviews (4-5 stars) → extract patterns
    - Recommend songs with matching genres/artists not in playlists
  - Advanced ML models (matrix factorization, embeddings) deferred to post-MVP
  - Daily batch update acceptable for MVP (real-time not required)
- **Implications**:
  - Recommendation service with simple scoring function
  - Database query optimization with proper indexes
  - Background job/cron for daily update (optional MVP)
  - Future: ML model integration point defined in architecture

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **Clean Architecture (Selected)** | Layered architecture: Routes → Services → Repositories → Models | Clear separation of concerns, testable business logic, framework independence | More boilerplate, learning curve for team | Aligns with steering TDD principles, scalable for future |
| MVC Pattern | Traditional Model-View-Controller | Simple, well-known | Tight coupling, fat controllers, hard to test | Not recommended for API-first applications |
| Vertical Slice Architecture | Feature-based slices with minimal sharing | Fast feature development, low coupling | Potential code duplication, harder to enforce standards | Better for smaller teams, harder with TDD |
| Microservices | Separate services per domain | Ultimate scalability, tech flexibility | Over-engineering for MVP, deployment complexity | Defer until scale requires it |

**Selected**: Clean Architecture with Service Layer
- Aligns with TDD (services easily testable)
- Framework-independent business logic
- Clear boundaries for parallel team work
- Scales from MVP to production

## Design Decisions

### Decision: Backend Architecture (Clean Architecture + Service Layer)
- **Context**: Need scalable, testable backend architecture for music catalog platform
- **Alternatives Considered**:
  1. Flat FastAPI routes with inline logic — simple but unmaintainable
  2. MVC pattern — tight coupling between models and views
  3. Clean Architecture with Service Layer — separation of concerns
- **Selected Approach**: Clean Architecture (Routes → Services → Repositories → Models)
  ```
  Routes: HTTP handlers (FastAPI routers)
  Services: Business logic (playlist creation, recommendation algorithm)
  Repositories: Data access (SQLAlchemy queries)
  Models: Domain entities (SQLAlchemy ORM models)
  ```
- **Rationale**: 
  - Business logic testable without FastAPI/database
  - TDD-friendly: write service tests first
  - Clear domain boundaries prevent merge conflicts
  - Framework-agnostic services enable future migrations
- **Trade-offs**: 
  - More boilerplate code vs direct database access
  - Steeper learning curve vs simple CRUD
- **Follow-up**: Validate service interface design during implementation

### Decision: Database Schema (Existing + Soft Delete Pattern)
- **Context**: Database schema provided at `/src/digital-music-store.sql`, need delete strategy
- **Alternatives Considered**:
  1. Hard delete — simple but data loss risk
  2. Soft delete with `deleted_at` column — keeps history
  3. Archive table pattern — separate tables for deleted records
- **Selected Approach**: Soft delete with `deleted_at TIMESTAMPTZ NULL`
- **Rationale**:
  - Requirement 4: "When song is deleted, Song Service shall perform soft delete"
  - Enables audit trail and undo functionality
  - Simpler than archive tables for MVP
- **Trade-offs**: Queries need `WHERE deleted_at IS NULL` filter
- **Follow-up**: Add index on `deleted_at` for performance

### Decision: Frontend State Management (React Context API)
- **Context**: Need state management for auth, playlists, current user
- **Alternatives Considered**:
  1. Redux — powerful but complex setup
  2. Zustand — simple, modern
  3. React Context API — built-in, no dependencies
- **Selected Approach**: React Context API with custom hooks
- **Rationale**:
  - MVP scope doesn't require Redux complexity
  - Auth context: `useAuth()` hook
  - User context: `useUser()` hook
  - Simple, testable, zero dependencies
- **Trade-offs**: 
  - Re-renders can be inefficient (use context splitting)
  - Redux provides better DevTools
- **Follow-up**: Monitor performance; migrate to Zustand if context re-renders become issue

### Decision: API Client (Axios vs Fetch API)
- **Context**: Frontend needs HTTP client for API communication
- **Alternatives Considered**:
  1. Fetch API — built-in, no dependencies
  2. Axios — interceptors, automatic JSON parsing
  3. React Query + Fetch — caching, loading states
- **Selected Approach**: Fetch API with custom wrapper + React Query (v5)
- **Rationale**:
  - Fetch API native, no extra bundle size
  - React Query handles caching, loading states, error handling
  - Custom `apiClient.ts` wrapper for auth headers, error handling
- **Trade-offs**: Fetch API more verbose than Axios
- **Follow-up**: Evaluate React Query integration during implementation

### Decision: JWT Storage (httpOnly Cookies vs LocalStorage)
- **Context**: Security requirement: protect JWT tokens from XSS attacks
- **Alternatives Considered**:
  1. LocalStorage — simple but vulnerable to XSS
  2. httpOnly Cookies — XSS-safe but needs CSRF protection
  3. Memory-only storage — most secure but loses on refresh
- **Selected Approach**: httpOnly Cookies with SameSite=Strict
- **Rationale**:
  - Security: httpOnly cookies inaccessible to JavaScript (XSS protection)
  - SameSite=Strict prevents CSRF attacks
  - Automatic cookie sending reduces client complexity
- **Trade-offs**: 
  - Requires backend cookie support
  - CORS configuration more complex
- **Follow-up**: Implement CSRF token for POST/PUT/DELETE if needed

### Decision: File Upload Strategy (Out of MVP Scope)
- **Context**: Requirements don't specify audio file uploads in MVP
- **Selected Approach**: Defer file upload to post-MVP; use external URLs for audio metadata
- **Rationale**:
  - MVP excludes audio streaming (per requirements update)
  - Song model includes metadata only (title, duration, external links)
  - Avoids S3/storage infrastructure in MVP
- **Trade-offs**: Admin must manage audio files externally
- **Follow-up**: Design file upload architecture for post-MVP streaming feature

## Risks & Mitigations

### Risk 1: Neon PostgreSQL Cold Start Latency
- **Description**: Serverless databases may have cold start delays affecting first request
- **Impact**: User perceives slow initial page load
- **Mitigation**: 
  - Implement connection warming in health check endpoint
  - Use Neon's connection pooling (always-on connection)
  - Frontend loading states with skeleton screens

### Risk 2: TDD Learning Curve for Team
- **Description**: Team may be unfamiliar with strict Red-Green-Refactor cycle
- **Impact**: Slower initial development velocity
- **Mitigation**:
  - Provide TDD training/examples in steering (`tdd.md`)
  - Pair programming for first few features
  - Code reviews enforce test-first approach
  - CI/CD blocks merges without test coverage

### Risk 3: Recommendation Algorithm Performance
- **Description**: Simple scoring algorithm may not scale beyond 100k songs
- **Impact**: Slow recommendation generation, poor user experience
- **Mitigation**:
  - Set 1-second timeout requirement (Requirement 7.12)
  - Implement database query optimization with indexes
  - Cache recommendation results (daily update acceptable)
  - Fallback to popular/trending songs if algorithm slow

### Risk 4: Frontend Bundle Size with Design System
- **Description**: Custom fonts, icons, Tailwind CSS may bloat bundle
- **Impact**: Slow page loads, poor Lighthouse score
- **Mitigation**:
  - Vite code splitting (route-based lazy loading)
  - Google Fonts with `font-display: swap`
  - Material Symbols via CSS instead of full icon font
  - Tailwind JIT mode (generates only used utilities)
  - Target: Lighthouse score >90 (Requirement 10.5)

### Risk 5: Rate Limiting Implementation Complexity
- **Description**: Requirements specify rate limiting (100 req/min unauthenticated, 1000 req/min authenticated)
- **Impact**: Without rate limiting, API vulnerable to abuse
- **Mitigation**:
  - Use slowapi library (FastAPI middleware for rate limiting)
  - Redis backend for distributed rate limiting (optional, in-memory for MVP)
  - Per-IP and per-user limits in middleware
  - Return 429 status with Retry-After header (Requirement 1.6)

## References

### Official Documentation
- [FastAPI Official Docs](https://fastapi.tiangolo.com/) - Async, dependency injection, security
- [SQLAlchemy 2.0 Docs](https://docs.sqlalchemy.org/en/20/) - Async ORM patterns
- [Neon PostgreSQL Docs](https://neon.tech/docs) - Serverless Postgres, connection pooling
- [React 18 Docs](https://react.dev/) - Concurrent features, hooks
- [Tailwind CSS Docs](https://tailwindcss.com/) - JIT mode, custom configuration
- [pytest Documentation](https://docs.pytest.org/) - Fixtures, async support
- [React Testing Library](https://testing-library.com/react) - Testing best practices

### Architecture Patterns
- Clean Architecture (Robert C. Martin) - Layered architecture principles
- Repository Pattern - Data access abstraction
- Service Layer Pattern - Business logic separation

### Security Resources
- OWASP Top 10 - Security vulnerabilities to avoid
- JWT Best Practices - Token expiration, secret management
- bcrypt Documentation - Password hashing cost factor recommendations

### Internal References
- `.sdd/steering/tech.md` - Technology stack and TDD guidelines
- `.sdd/steering/requirements.md` - EARS pattern documentation
- `.sdd/steering/tdd.md` - Test-Driven Development workflow
- `/src/stitch/stitch/neon_groove/DESIGN.md` - Visual design system specification
- `/src/digital-music-store.sql` - Database schema definition
