# Test-Driven Development (TDD)

## Mandatory Methodology

TDD is the **required development approach** for all implementation work in this project. No code shall be written without tests first.

## Core Principle

> "Tests are the specification. Code is the implementation."

Every EARS requirement SHALL statement must have corresponding test(s) written BEFORE the implementation code.

## Red-Green-Refactor Cycle

### 1. Red Phase - Write Failing Test

**Goal**: Define expected behavior through tests

**Process**:
1. Read EARS requirement from requirements.md
2. Identify the SHALL statement(s) to implement
3. Write test(s) that verify the behavior
4. Run test suite → confirm test FAILS (Red)
5. Commit: `test: add failing test for <feature>`

**Example (Backend - Python/pytest):**
```python
# tests/integration/test_artists_api.py
# EARS: When authenticated admin creates artist record, 
#       the Artist Service shall validate artist name is 1-200 characters

@pytest.mark.asyncio
async def test_create_artist_validates_name_length(client, admin_token):
    """Red phase - This test will fail initially"""
    # Test empty name
    response = await client.post(
        "/api/v1/artists",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "", "country": "US"}
    )
    assert response.status_code == 400
    assert "name" in response.json()["detail"]
    
    # Test name too long (201 characters)
    long_name = "A" * 201
    response = await client.post(
        "/api/v1/artists",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": long_name, "country": "US"}
    )
    assert response.status_code == 400
    
    # Test valid name
    response = await client.post(
        "/api/v1/artists",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"name": "Valid Artist", "country": "US"}
    )
    assert response.status_code == 201
```

**Example (Frontend - React/Jest):**
```javascript
// src/components/ArtistForm.test.tsx
// EARS: When user searches artists by name, 
//       the Artist Service shall perform case-insensitive partial match

test('search artists performs case-insensitive match', async () => {
  // Mock API response
  const mockArtists = [
    { id: 1, name: 'The Beatles' },
    { id: 2, name: 'Beatles Cover Band' }
  ];
  
  jest.spyOn(artistApi, 'search').mockResolvedValue(mockArtists);
  
  render(<ArtistSearch />);
  
  // Type lowercase search
  const searchInput = screen.getByRole('textbox', { name: /search/i });
  await userEvent.type(searchInput, 'beatles');
  
  // Should find both artists (case-insensitive)
  await waitFor(() => {
    expect(screen.getByText('The Beatles')).toBeInTheDocument();
    expect(screen.getByText('Beatles Cover Band')).toBeInTheDocument();
  });
  
  expect(artistApi.search).toHaveBeenCalledWith({ query: 'beatles' });
});
```

### 2. Green Phase - Minimal Implementation

**Goal**: Make the test pass with simplest possible code

**Process**:
1. Write minimal code to satisfy test
2. No optimization, no extra features
3. Run test suite → confirm test PASSES (Green)
4. Do NOT refactor yet
5. Commit: `feat: implement <feature> to pass test`

**Example (Backend Implementation):**
```python
# app/routers/artists.py
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, validator

class ArtistCreate(BaseModel):
    name: str
    country: str
    
    @validator('name')
    def validate_name_length(cls, v):
        if len(v) < 1 or len(v) > 200:
            raise ValueError('name must be between 1 and 200 characters')
        return v

@router.post("/artists", status_code=status.HTTP_201_CREATED)
async def create_artist(
    artist: ArtistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    # Minimal implementation - just enough to pass test
    db_artist = Artist(name=artist.name, country=artist.country)
    db.add(db_artist)
    db.commit()
    db.refresh(db_artist)
    return db_artist
```

**Example (Frontend Implementation):**
```typescript
// src/services/artistApi.ts
export const artistApi = {
  async search(params: { query: string }) {
    const response = await fetch(
      `/api/v1/artists/search?q=${encodeURIComponent(params.query)}`
    );
    return response.json();
  }
};

// src/components/ArtistSearch.tsx
export function ArtistSearch() {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  
  const handleSearch = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setQuery(value);
    
    if (value.length >= 2) {
      const artists = await artistApi.search({ query: value });
      setResults(artists);
    }
  };
  
  return (
    <div>
      <input 
        type="text" 
        aria-label="search artists"
        value={query}
        onChange={handleSearch}
      />
      <ul>
        {results.map(artist => (
          <li key={artist.id}>{artist.name}</li>
        ))}
      </ul>
    </div>
  );
}
```

### 3. Refactor Phase - Improve Quality

**Goal**: Clean up code while maintaining green tests

**Process**:
1. Identify code smells, duplication, complexity
2. Refactor implementation (NOT tests)
3. Run test suite after each change → keep GREEN
4. Commit: `refactor: improve <feature> implementation`

**Example (Backend Refactoring):**
```python
# app/services/artist_service.py
# Extracted business logic into service layer

class ArtistService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_artist(self, name: str, country: str) -> Artist:
        """Create new artist with validation"""
        self._validate_name(name)
        self._validate_country(country)
        
        artist = Artist(name=name, country=country)
        self.db.add(artist)
        self.db.commit()
        self.db.refresh(artist)
        return artist
    
    def _validate_name(self, name: str):
        if not 1 <= len(name) <= 200:
            raise ValidationError("Artist name must be 1-200 characters")
    
    def _validate_country(self, country: str):
        if not self._is_valid_iso_country(country):
            raise ValidationError("Invalid country code")
    
    def _is_valid_iso_country(self, code: str) -> bool:
        # ISO 3166-1 alpha-2 validation
        return len(code) == 2 and code.isalpha()

# app/routers/artists.py - Now cleaner
@router.post("/artists", status_code=status.HTTP_201_CREATED)
async def create_artist(
    artist: ArtistCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    service = ArtistService(db)
    return service.create_artist(artist.name, artist.country)
```

## Test Types & Strategies

### Unit Tests

**Purpose**: Test business logic in isolation  
**Speed**: Fast (milliseconds)  
**Coverage**: 80%+ required

**Backend Example:**
```python
# tests/unit/test_password_service.py
def test_hash_password_uses_bcrypt():
    password = "SecurePass123!"
    hashed = hash_password(password)
    
    assert hashed != password
    assert bcrypt.checkpw(password.encode(), hashed)

def test_validate_password_strength_rejects_weak():
    weak_passwords = ["short", "nodigit", "NoSpecial1"]
    
    for pwd in weak_passwords:
        with pytest.raises(ValidationError):
            validate_password_strength(pwd)
```

**Frontend Example:**
```javascript
// src/utils/validation.test.ts
describe('validateEmail', () => {
  test('accepts valid email formats', () => {
    expect(validateEmail('user@example.com')).toBe(true);
    expect(validateEmail('name+tag@domain.co.uk')).toBe(true);
  });
  
  test('rejects invalid email formats', () => {
    expect(validateEmail('notanemail')).toBe(false);
    expect(validateEmail('@nodomain.com')).toBe(false);
  });
});
```

### Integration Tests

**Purpose**: Test API endpoints with database  
**Speed**: Medium (seconds)  
**Coverage**: All API endpoints

**Backend Example:**
```python
# tests/integration/test_playlist_api.py
@pytest.mark.asyncio
async def test_create_playlist_workflow(client, authenticated_user, db_session):
    # Create playlist
    response = await client.post(
        "/api/v1/playlists",
        headers=authenticated_user.headers,
        json={"title": "My Playlist"}
    )
    assert response.status_code == 201
    playlist_id = response.json()["id"]
    
    # Add songs to playlist
    response = await client.post(
        f"/api/v1/playlists/{playlist_id}/songs",
        headers=authenticated_user.headers,
        json={"song_id": 1}
    )
    assert response.status_code == 200
    
    # Retrieve playlist with songs
    response = await client.get(
        f"/api/v1/playlists/{playlist_id}",
        headers=authenticated_user.headers
    )
    assert response.status_code == 200
    assert len(response.json()["songs"]) == 1
```

### E2E Tests

**Purpose**: Test critical user flows  
**Speed**: Slow (minutes)  
**Coverage**: Happy paths + critical errors

**Frontend Example (Cypress):**
```javascript
// e2e/create-playlist.spec.ts
describe('Create and manage playlist', () => {
  beforeEach(() => {
    cy.login('user@example.com', 'password');
    cy.visit('/playlists');
  });
  
  it('creates playlist and adds songs', () => {
    // Create playlist
    cy.get('[data-cy=create-playlist]').click();
    cy.get('[data-cy=playlist-title]').type('My Favorites');
    cy.get('[data-cy=save-playlist]').click();
    
    // Verify creation
    cy.contains('My Favorites').should('be.visible');
    
    // Add song to playlist
    cy.visit('/explore');
    cy.get('[data-cy=song-item]').first().within(() => {
      cy.get('[data-cy=add-to-playlist]').click();
    });
    cy.get('[data-cy=playlist-selector]').contains('My Favorites').click();
    
    // Verify song added
    cy.visit('/playlists');
    cy.contains('My Favorites').click();
    cy.get('[data-cy=playlist-songs]').should('have.length', 1);
  });
});
```

## Test Fixtures & Factories

### Backend (pytest + factory_boy)

```python
# tests/fixtures/factories.py
import factory
from app.models import Artist, Album, Song, User

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db_session
    
    email = factory.Sequence(lambda n: f"user{n}@example.com")
    password = factory.PostGenerationMethodCall('set_password', 'password123')
    role = "user"

class ArtistFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Artist
        sqlalchemy_session = db_session
    
    name = factory.Sequence(lambda n: f"Artist {n}")
    country = "US"

class SongFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = Song
        sqlalchemy_session = db_session
    
    title = factory.Sequence(lambda n: f"Song {n}")
    album = factory.SubFactory(AlbumFactory)
    duration_seconds = 180

# Usage in tests
def test_create_review_for_song(db_session):
    song = SongFactory.create()
    user = UserFactory.create()
    
    review = Review(
        user_id=user.id,
        song_id=song.id,
        rating=5,
        body="Great song!"
    )
    db_session.add(review)
    db_session.commit()
    
    assert review.id is not None
```

### Frontend (MSW - Mock Service Worker)

```javascript
// src/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/v1/artists', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        items: [
          { id: 1, name: 'Test Artist', country: 'US' },
        ],
        total: 1
      })
    );
  }),
  
  rest.post('/api/v1/artists', (req, res, ctx) => {
    const { name, country } = req.body;
    return res(
      ctx.status(201),
      ctx.json({ id: 1, name, country })
    );
  }),
];

// setupTests.ts
import { setupServer } from 'msw/node';
import { handlers } from './mocks/handlers';

const server = setupServer(...handlers);

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

## Coverage Requirements

### Minimum Thresholds

**Backend:**
- Line coverage: 80%
- Branch coverage: 75%
- Critical paths (auth, security): 95%

**Frontend:**
- Line coverage: 70%
- Component coverage: 80%
- Critical flows (auth, checkout): 90%

### Running Coverage

**Backend:**
```bash
# Run tests with coverage
pytest --cov=app --cov-report=html --cov-report=term

# Fail if below threshold
pytest --cov=app --cov-fail-under=80
```

**Frontend:**
```bash
# Run tests with coverage
npm test -- --coverage

# View HTML report
open coverage/lcov-report/index.html
```

### Coverage Configuration

**Backend (pytest.ini):**
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --cov=app
    --cov-fail-under=80
    --cov-report=term-missing
    --cov-report=html
```

**Frontend (package.json):**
```json
{
  "jest": {
    "coverageThreshold": {
      "global": {
        "lines": 70,
        "statements": 70,
        "branches": 65,
        "functions": 70
      }
    },
    "collectCoverageFrom": [
      "src/**/*.{ts,tsx}",
      "!src/**/*.d.ts",
      "!src/mocks/**"
    ]
  }
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
# .github/workflows/test.yml
name: Test Suite

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov
      - name: Run tests
        run: pytest --cov=app --cov-fail-under=80
      - name: Upload coverage
        uses: codecov/codecov-action@v3
  
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm test -- --coverage
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

## TDD Best Practices

### Do's ✅

1. **Write tests first** - Always red before green
2. **Test behavior, not implementation** - Focus on what, not how
3. **Keep tests simple** - One assertion per concept
4. **Use descriptive names** - Test name explains scenario
5. **Isolate tests** - No dependencies between tests
6. **Fast feedback** - Unit tests should run in milliseconds
7. **Refactor regularly** - Keep code and tests clean

### Don'ts ❌

1. **Don't skip red phase** - Never write code without failing test
2. **Don't test private methods** - Test public interface
3. **Don't write brittle tests** - Avoid testing implementation details
4. **Don't share state** - Each test should be independent
5. **Don't ignore failing tests** - Fix or remove, never skip
6. **Don't mock everything** - Use real objects when possible
7. **Don't write tests after code** - TDD means tests FIRST

## Mapping EARS to Tests

### Process

1. Read EARS requirement
2. Identify each SHALL statement
3. Write test for each statement
4. Include alternative flows
5. Include error handling

### Example Mapping

**EARS Requirement:**
```
WHEN authenticated user creates playlist
THEN system SHALL validate playlist title is 1-200 characters
WHERE user is authenticated

[Alternative Flows]
WHEN playlist title is empty
THEN system SHALL return 400 Bad Request

[Error Handling]
IF user is not authenticated
THEN system SHALL return 401 Unauthorized
```

**Test Implementation:**
```python
class TestCreatePlaylist:
    def test_creates_playlist_with_valid_title(self, client, auth_user):
        """Main flow: SHALL validate title 1-200 chars"""
        response = client.post(
            "/api/v1/playlists",
            headers=auth_user.headers,
            json={"title": "My Playlist"}
        )
        assert response.status_code == 201
        assert response.json()["title"] == "My Playlist"
    
    def test_rejects_empty_title(self, client, auth_user):
        """Alternative flow: empty title"""
        response = client.post(
            "/api/v1/playlists",
            headers=auth_user.headers,
            json={"title": ""}
        )
        assert response.status_code == 400
    
    def test_rejects_title_too_long(self, client, auth_user):
        """Alternative flow: title > 200 chars"""
        long_title = "A" * 201
        response = client.post(
            "/api/v1/playlists",
            headers=auth_user.headers,
            json={"title": long_title}
        )
        assert response.status_code == 400
    
    def test_requires_authentication(self, client):
        """Error handling: not authenticated"""
        response = client.post(
            "/api/v1/playlists",
            json={"title": "My Playlist"}
        )
        assert response.status_code == 401
```

---

**Remember:** TDD is not about testing. It's about **designing** software through tests. Tests are the specification, code is the implementation.
