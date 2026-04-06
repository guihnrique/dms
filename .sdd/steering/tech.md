# Technology Stack

## Architecture

**Full-Stack Application**: React frontend + Python backend with PostgreSQL database
- **Design Phase**: HTML/CSS mockups (Stitch prototypes in `/src/stitch/`)
- **Implementation Phase**: React SPA + Python REST API

## Core Technologies

### Frontend
- **Framework**: React (with hooks and functional components)
- **Language**: JavaScript/TypeScript
- **CSS Framework**: Tailwind CSS (with custom "Neon Groove" configuration)
- **Build Tool**: Vite or Create React App
- **State Management**: React Context API or Redux (TBD based on complexity)
- **Fonts**: 
  - Space Grotesk (Headlines/Display)
  - Manrope (Body/Labels)
  - Material Symbols Outlined (Icons)

### Backend
- **Language**: Python 3.10+
- **Framework**: FastAPI or Flask (REST API)
- **ORM**: SQLAlchemy
- **Authentication**: JWT-based authentication
- **API Documentation**: OpenAPI/Swagger (auto-generated)

### Database
- **RDBMS**: PostgreSQL (hosted on Neon - https://neon.tech)
- **Schema**: 5-table relational model (`src/digital-music-store.sql`)
  - `artists` - Music artists with country metadata
  - `albums` - Albums linked to artists
  - `songs` - Individual tracks linked to albums
  - `playlists` - User-created playlists
  - `reviews` - User reviews/ratings for songs
- **Timestamps**: All tables include `created_at` and `updated_at` (TIMESTAMPTZ)

## Design System: "Neon Groove"

### Visual Philosophy
**Creative North Star**: "The Neon Pulse" - Interface as living digital venue, not static grid

### Color Architecture
- **Base**: Deep nocturnal (`#1b0424`)
- **Surface Hierarchy**: Tonal layering system (`surface_container_low`, `surface_container`, `surface_bright`)
- **Accents**: Neon gradients (primary `#a533ff` to secondary `#00d2fd`)
- **No-Line Rule**: Borders forbidden; boundaries through background shifts and tonal transitions

### Key Technical Decisions

**1. Glassmorphism Over Shadows**
- Navigation and floating elements use backdrop-blur (20-24px)
- 60% opacity with ghost borders for glass effect
- Depth through color shifts, not traditional shadows

**2. Gradient-First Interactivity**
- Primary actions use electric gradients (`primary-dim` to `secondary`)
- Progress bars and active states use dual-tone gradients

**3. Typography Hierarchy**
- Display (3.5rem) for major content (artist names, promotions)
- Title/Body with clear metadata separation (`on_surface_variant`)
- High contrast for dark background legibility

**4. Component Standards**
- Buttons: Rounded full (9999px) for primary, glass for secondary
- Cards: XL radius (1.5rem), no dividers, hover scale (1.02x)
- Inputs: Minimalist, bottom-accent focus (2px primary)

## Development Standards

### Documentation Quality
- **Requirements**: MUST follow EARS pattern (see `.sdd/steering/requirements.md`)
  - WHEN [trigger] THEN [action] SHALL WHERE [constraints]
  - Include Alternative Flows and Error Handling
  - Every requirement must be testable and atomic

### Development Methodology
- **TDD (Test-Driven Development)**: MANDATORY approach for all implementation
  - Write tests BEFORE implementation code
  - Follow Red-Green-Refactor cycle:
    1. **Red**: Write failing test that defines desired behavior
    2. **Green**: Write minimal code to make test pass
    3. **Refactor**: Improve code while keeping tests green
  - Every EARS requirement SHALL statement must map to test case(s)
  - Minimum test coverage: 80% for backend, 70% for frontend
  - Unit tests for business logic, integration tests for API endpoints
  - E2E tests for critical user flows

### Code Quality
- **React**: Functional components with hooks, component composition pattern
- **Python**: PEP 8 style guide, type hints required
- **CSS**: Tailwind utility-first, custom theme configuration via `tailwind.config`
- **Mobile-first responsive design**
- **API**: RESTful design principles, consistent naming

### Security Requirements
**CRITICAL - Always verify library security before use:**
- Check dependencies for known vulnerabilities (npm audit, pip-audit, Snyk)
- Keep all packages updated to latest stable versions
- Review security advisories for React, Python frameworks, and database drivers
- Never commit secrets, API keys, or credentials to version control
- Use environment variables for sensitive configuration
- Implement input validation and sanitization (SQL injection, XSS prevention)
- Apply principle of least privilege for database access
- Use parameterized queries/ORM to prevent SQL injection
- Implement rate limiting on API endpoints
- Enable CORS with specific allowed origins (not wildcard)
- Use HTTPS for all production traffic
- Hash passwords with bcrypt or Argon2 (never plain text)

### Design Constraints
- **No pure black** (#000000) - use deep violet base
- **No 90-degree corners** - minimum `md` (0.75rem) radius
- **No standard icons** - thin-stroke (1.5px) custom icons
- **Spacing Scale**: 12px and 16px for major sections

### Accessibility
- Ghost borders (`outline_variant` 15% opacity) as fallback
- High contrast ratios on dark backgrounds
- Semantic HTML for screen readers
- ARIA labels for interactive elements

## Development Environment

### Required Tools
- **Frontend**: Node.js 18+, npm/yarn, React DevTools
- **Backend**: Python 3.10+, pip, virtualenv/venv
- **Database**: PostgreSQL client, Neon CLI
- **Version Control**: Git
- **API Testing**: Postman, curl, or httpie
- **Testing Frameworks**:
  - **Frontend**: Jest + React Testing Library (unit), Vitest (alternative), Cypress or Playwright (E2E)
  - **Backend**: pytest (unit/integration), pytest-cov (coverage), pytest-asyncio (async tests)
  - **API Testing**: pytest with httpx or requests, factory_boy for fixtures
  - **Database Testing**: pytest-postgresql or testcontainers for isolated DB tests

### Environment Variables Pattern
```bash
# .env (never commit to git)
DATABASE_URL=postgresql://user:pass@neon.tech/dbname
JWT_SECRET=<secure-random-string>
API_PORT=8000
FRONTEND_URL=http://localhost:3000
```

### Common Patterns

**React Components:**
```jsx
// Glassmorphism utility class
className="backdrop-blur-xl bg-white/5"

// Surface layering
className="bg-surface-container-low hover:bg-surface-container"

// Interactive gradient button
className="bg-gradient-to-r from-primary-dim to-secondary"
```

**Python API:**
```python
# FastAPI route pattern
@router.get("/artists/{artist_id}")
async def get_artist(artist_id: int, db: Session = Depends(get_db)):
    # Input validation, error handling
    return artist_schema
```

## Test-Driven Development (TDD) Standards

### TDD Workflow (Red-Green-Refactor)

**MANDATORY for all implementation work:**

1. **Red Phase - Write Failing Test**
   - Read EARS requirement from requirements.md
   - Write test(s) that verify the SHALL statement(s)
   - Run test → confirm it fails (RED)
   - Commit: `test: add failing test for [feature]`

2. **Green Phase - Make Test Pass**
   - Write minimal code to satisfy the test
   - Run test → confirm it passes (GREEN)
   - Do NOT refactor yet
   - Commit: `feat: implement [feature] to pass test`

3. **Refactor Phase - Improve Code**
   - Improve code quality, remove duplication
   - Keep tests passing (stay GREEN)
   - Commit: `refactor: improve [feature] implementation`

### Test Types by Layer

**Backend (Python/FastAPI):**
```python
# Unit Tests - Business logic in isolation
def test_hash_password_with_bcrypt():
    result = hash_password("MyPass123!")
    assert bcrypt.checkpw("MyPass123!", result)

# Integration Tests - API endpoints with database
@pytest.mark.asyncio
async def test_create_artist_returns_201(client, db_session):
    response = await client.post("/api/v1/artists", json={"name": "Artist"})
    assert response.status_code == 201

# Repository Tests - Database operations
def test_artist_repository_find_by_name(db_session):
    artist = ArtistRepository.find_by_name("Test Artist")
    assert artist.name == "Test Artist"
```

**Frontend (React/Jest):**
```javascript
// Unit Tests - Component logic
test('Button shows loading state when clicked', () => {
  render(<Button onClick={mockFn}>Click</Button>);
  fireEvent.click(screen.getByRole('button'));
  expect(screen.getByText('Loading...')).toBeInTheDocument();
});

// Integration Tests - Component interactions
test('Login form submits credentials', async () => {
  render(<LoginForm onSubmit={mockSubmit} />);
  // Fill form and submit
  await waitFor(() => expect(mockSubmit).toHaveBeenCalled());
});

// E2E Tests - Critical user flows (Cypress/Playwright)
describe('User can create playlist', () => {
  it('creates new playlist with songs', () => {
    cy.visit('/playlists');
    cy.get('[data-cy=create-playlist]').click();
    // Complete flow...
  });
});
```

### Test Coverage Requirements

**Minimum Coverage:**
- Backend: 80% line coverage
- Frontend: 70% line coverage
- Critical paths: 95% coverage (auth, payments in future)

**Coverage Tools:**
- Backend: pytest-cov (`pytest --cov=app --cov-report=html`)
- Frontend: Jest built-in (`npm test -- --coverage`)

### Test Organization

**Backend Structure:**
```
backend/
├── tests/
│   ├── unit/              # Pure business logic
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/       # API + Database
│   │   ├── test_artists_api.py
│   │   ├── test_albums_api.py
│   │   └── conftest.py    # Fixtures
│   └── fixtures/          # Shared test data
│       └── factories.py   # factory_boy factories
```

**Frontend Structure:**
```
frontend/
├── src/
│   └── components/
│       ├── Button.tsx
│       └── Button.test.tsx     # Co-located tests
└── e2e/
    └── playlists.spec.ts       # E2E tests
```

### Test Naming Convention

- **Unit tests**: `test_<function_name>_<scenario>`
  - Example: `test_validate_email_rejects_invalid_format`
- **Integration tests**: `test_<endpoint>_<expected_result>`
  - Example: `test_post_artists_returns_201_with_valid_data`
- **E2E tests**: Natural language
  - Example: `User can create and share a playlist`

### TDD Anti-Patterns (Avoid)

❌ Writing implementation before tests  
❌ Tests that test implementation details instead of behavior  
❌ Skipping refactor phase  
❌ Large test files (split by feature)  
❌ Tests with external dependencies (use mocks/fixtures)  
❌ Flaky tests (non-deterministic results)  

### CI/CD Integration

**Automated Testing Pipeline:**
1. On git push → Run all tests
2. Coverage report → Fail if below threshold
3. Lint checks → Fail if standards violated
4. All green → Allow merge

## Project Phases

### Phase 1: Design (Completed)
Stitch-generated HTML screens demonstrating visual patterns

### Phase 2: Implementation (Current - TDD Approach)
- **Requirements → Tests → Code** (TDD cycle mandatory)
- React frontend consuming REST API
- Python backend with FastAPI/Flask
- PostgreSQL database on Neon
- Schema: `/src/digital-music-store.sql`
- Minimum 80% backend, 70% frontend test coverage

### Phase 3: Enhancement (Future)
- Audio streaming integration
- Recommendation algorithm refinement
- Payment processing

---
_Document standards and patterns, not every dependency_
