# Requirements Standards

## EARS Pattern (Easy Approach to Requirements Syntax)

All requirement documents MUST follow the EARS template for clarity, consistency, and testability.

## Core EARS Structure

### Basic Pattern
```
WHEN [trigger/pre conditions]
THEN [response/action] SHALL
WHERE [constraints/conditions]
```

### Complete Pattern with Flows
```
WHEN [trigger/pre conditions]
THEN [response/action] SHALL
WHERE [constraints/conditions]

[Alternative Flows]
WHEN [alternative trigger]
THEN [alternative action] SHALL

[Error Handling]
IF <condition> THEN [error response] SHALL
```

## EARS Keywords

- **WHEN**: Trigger condition or precondition that activates the requirement
- **THEN**: System response or action (mandatory behavior)
- **SHALL**: Indicates mandatory requirement (use consistently)
- **WHERE**: Constraints, boundary conditions, or context
- **IF**: Conditional logic for error handling or branching

## Requirement Categories

### 1. Ubiquitous Requirements
**Pattern**: System SHALL [action]
```
System SHALL hash all user passwords using bcrypt with minimum cost factor of 12
```

### 2. Event-Driven Requirements
**Pattern**: WHEN [event] THEN system SHALL [response]
```
WHEN user submits login form
THEN system SHALL validate credentials against database
WHERE password match uses bcrypt comparison
```

### 3. State-Driven Requirements
**Pattern**: WHILE [state] system SHALL [behavior]
```
WHILE user is authenticated
THEN system SHALL include JWT token in all API requests
WHERE token expires after 24 hours
```

### 4. Optional Features
**Pattern**: WHERE [condition], system SHALL [behavior]
```
WHERE user is VIP member
THEN system SHALL enable high-quality audio streaming
```

### 5. Unwanted Behaviors
**Pattern**: IF [condition] THEN system SHALL NOT [forbidden action]
```
IF password validation fails
THEN system SHALL NOT reveal whether username or password is incorrect
```

## Complete Requirement Example

### User Authentication Requirement
```
WHEN user submits login credentials
THEN system SHALL authenticate user
WHERE:
  - Username is valid email format
  - Password is at least 8 characters
  - Rate limit: maximum 5 attempts per 15 minutes

[Alternative Flows]
WHEN user provides valid OAuth token
THEN system SHALL authenticate via OAuth provider
WHERE provider is Google, Facebook, or GitHub

[Error Handling]
IF credentials are invalid
THEN system SHALL return generic "Invalid credentials" error
AND system SHALL NOT reveal which field is incorrect

IF rate limit exceeded
THEN system SHALL return 429 status code
AND system SHALL include Retry-After header

IF database connection fails
THEN system SHALL return 503 status code
AND system SHALL log error with correlation ID
```

## Requirements for Each Entity

When writing requirements in `requirements.md` files within `.sdd/specs/`, organize by:

1. **Functional Requirements**: Core business logic (EARS pattern)
2. **Data Requirements**: Schema, validation, relationships
3. **API Requirements**: Endpoints, request/response format
4. **Security Requirements**: Authentication, authorization, validation
5. **Performance Requirements**: Response times, throughput, scalability
6. **Error Handling**: Expected failures and recovery

## Anti-Patterns (Avoid These)

❌ **Vague**: "System should be fast"
✅ **EARS**: "WHERE dataset contains < 10,000 records THEN system SHALL return search results within 200ms"

❌ **Ambiguous**: "System handles errors properly"
✅ **EARS**: "IF database query fails THEN system SHALL return 500 status code AND log error with stack trace"

❌ **Implementation detail**: "System uses bcrypt library"
✅ **EARS**: "System SHALL hash passwords using industry-standard algorithm with minimum cost factor 12"

## Quality Checklist

Each requirement SHALL be:
- [ ] **Testable**: Can be verified with pass/fail test
- [ ] **Atomic**: Describes one behavior
- [ ] **Unambiguous**: No room for interpretation
- [ ] **Complete**: Includes main flow + alternatives + errors
- [ ] **Consistent**: Uses EARS keywords correctly
- [ ] **Traceable**: Links to design decisions and implementation

## Integration with SDD Workflow

### During `/sdd:spec-requirements`
- Generate requirements.md using EARS pattern
- Organize by functional areas
- Include all WHEN/THEN/WHERE/IF clauses
- Cover happy paths AND error scenarios

### During `/sdd:spec-design`
- Map EARS requirements to technical design decisions
- Ensure design addresses all SHALL statements
- Document how constraints (WHERE clauses) are enforced

### During `/sdd:spec-tasks`
- Break down each EARS requirement into implementation tasks
- Create tests that verify SHALL statements
- Ensure error handling (IF clauses) becomes test cases

### During `/sdd:validate-impl`
- Verify each SHALL statement is implemented
- Check all error scenarios (IF clauses) are handled
- Confirm constraints (WHERE clauses) are enforced

## Example: Album Management Feature

```markdown
# Requirements: Album Management

## FR-1: Create Album
WHEN authenticated user submits new album data
THEN system SHALL create album record in database
WHERE:
  - User has artist role or admin role
  - Album title is 1-200 characters
  - Artist ID exists in database
  - Release year is between 1900 and current year + 1

[Alternative Flows]
WHEN album with same title and artist already exists
THEN system SHALL return existing album
AND system SHALL set HTTP status 200 (not 201)

[Error Handling]
IF user lacks artist/admin role
THEN system SHALL return 403 Forbidden

IF artist_id does not exist
THEN system SHALL return 400 Bad Request
AND system SHALL include message "Artist not found"

IF database constraint violation occurs
THEN system SHALL return 409 Conflict
AND system SHALL log full error details

## FR-2: List Albums
WHEN user requests album listing
THEN system SHALL return paginated album list
WHERE:
  - Default page size is 20 albums
  - Maximum page size is 100 albums
  - Results ordered by release_year DESC, title ASC
  - Response time < 500ms for collections up to 100,000 records

[Alternative Flows]
WHEN user provides artist_id filter
THEN system SHALL return only albums by that artist

WHEN user provides genre filter
THEN system SHALL return albums matching genre
WHERE genre is case-insensitive match

[Error Handling]
IF page number exceeds available pages
THEN system SHALL return empty results array
AND system SHALL include total_pages in response

IF page_size exceeds 100
THEN system SHALL return 400 Bad Request
```

---
_EARS pattern ensures requirements are clear, testable, and implementation-ready_
