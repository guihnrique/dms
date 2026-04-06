# Research & Design Decisions

## Summary
- **Feature**: `auth-security-foundation`
- **Discovery Scope**: New Feature (Greenfield Security Infrastructure)
- **Key Findings**:
  - FastAPI OAuth2PasswordBearer provides standard JWT flow with dependency injection
  - bcrypt cost factor 12 balances security and performance (250ms hash time)
  - slowapi library provides FastAPI-compatible rate limiting with Redis or in-memory backend
  - httpOnly cookies with SameSite=Strict prevents both XSS and CSRF attacks
  - Pydantic validation prevents injection attacks at API boundary

## Research Log

### FastAPI JWT Authentication Pattern
- **Context**: Need secure, standards-compliant JWT authentication for The Sonic Immersive platform
- **Sources Consulted**:
  - FastAPI Security documentation (OAuth2PasswordBearer, dependencies)
  - python-jose library (JWT signing, HS256 algorithm)
  - JWT.io specifications (claims, expiration)
- **Findings**:
  - FastAPI `OAuth2PasswordBearer` provides automatic token extraction from `Authorization: Bearer <token>` header
  - `python-jose` supports HS256 signing algorithm (symmetric key, sufficient for single-instance deployment)
  - Dependency injection pattern: `current_user = Depends(get_current_user)` for route protection
  - Token payload structure: `{"sub": user_id, "email": user@example.com, "role": "user", "exp": timestamp}`
  - Token expiration handled automatically by `python-jose` (raises `JWTError` on expired tokens)
- **Implications**:
  - AuthService generates JWT with 24-hour expiration
  - Middleware extracts and validates token via dependency injection
  - Role-based access control (RBAC) enforced through custom dependency: `Depends(require_role("admin"))`

### bcrypt Password Hashing Cost Factor
- **Context**: Steering specifies bcrypt cost factor minimum 12, need to validate performance impact
- **Sources Consulted**:
  - bcrypt library documentation (Python `bcrypt` package)
  - OWASP password storage recommendations
  - Performance benchmarks for cost factors 10, 12, 14
- **Findings**:
  - bcrypt cost factor 12: ~250ms hash time (acceptable for login)
  - bcrypt cost factor 14: ~1000ms hash time (too slow for user experience)
  - `bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))` for hashing
  - `bcrypt.checkpw(password.encode(), hashed)` for verification
  - Cost factor doubles computation per increment (cost 13 = 2x cost 12)
- **Implications**:
  - Use cost factor 12 as specified in steering
  - PasswordService encapsulates bcrypt operations
  - Hash verification happens during login (synchronous, blocking call acceptable)

### Rate Limiting Implementation
- **Context**: Requirements specify 100 req/min (unauthenticated), 1000 req/min (authenticated)
- **Sources Consulted**:
  - slowapi library (FastAPI rate limiting middleware)
  - FastAPI-limiter alternatives
  - Redis vs in-memory backend performance
- **Findings**:
  - `slowapi` integrates cleanly with FastAPI via middleware
  - Supports key functions: IP-based (unauthenticated) and user-based (authenticated) limiting
  - In-memory backend sufficient for MVP single-instance deployment
  - Redis backend required for horizontal scaling (future)
  - Rate limit headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`
  - Returns 429 status with `Retry-After` header when limit exceeded
- **Implications**:
  - Use slowapi with in-memory backend for MVP
  - Custom key function: `lambda request: request.client.host if not authenticated else user_id`
  - Middleware applied at API Gateway level (before routing)

### CORS Configuration
- **Context**: Frontend React app needs secure cross-origin requests to FastAPI backend
- **Sources Consulted**:
  - FastAPI CORS middleware documentation
  - CORS specification (MDN Web Docs)
  - Security best practices for CORS
- **Findings**:
  - FastAPI `CORSMiddleware` provides standard CORS handling
  - `allow_origins` parameter: List of specific origins (NO wildcard `*`)
  - `allow_credentials=True` required for httpOnly cookies
  - `allow_methods`: ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
  - `allow_headers`: ["Content-Type", "Authorization", "Accept"]
  - `max_age=86400` (24 hours) for preflight caching
- **Implications**:
  - `FRONTEND_URL` environment variable defines allowed origin
  - Middleware configuration in main FastAPI app initialization
  - Preflight OPTIONS requests handled automatically

### CSRF Protection Strategy
- **Context**: httpOnly cookies require CSRF protection for state-changing operations
- **Sources Consulted**:
  - OWASP CSRF Prevention Cheat Sheet
  - FastAPI CSRF middleware options
  - Double-submit cookie pattern
- **Findings**:
  - **Double-submit cookie pattern**: CSRF token in both cookie and custom header
  - Token generation: `secrets.token_urlsafe(32)` (cryptographically secure)
  - Token validation: Compare cookie value with header value (must match)
  - CSRF protection NOT required for: GET, HEAD, OPTIONS methods
  - Token expiration: 1 hour of inactivity
- **Implications**:
  - Middleware generates CSRF token and sets cookie on first request
  - Frontend reads cookie and includes token in custom header: `X-CSRF-Token`
  - Middleware validates token on POST/PUT/PATCH/DELETE methods

### JWT Storage: httpOnly Cookies vs LocalStorage
- **Context**: Security requirement to prevent XSS attacks on JWT tokens
- **Sources Consulted**:
  - OWASP Token Storage recommendations
  - Browser security model (httpOnly, secure, SameSite flags)
- **Findings**:
  - **LocalStorage**: Vulnerable to XSS (JavaScript can access tokens)
  - **httpOnly Cookies**: Inaccessible to JavaScript, automatic sending
  - **SameSite=Strict**: Prevents CSRF attacks (cookies only sent on same-site requests)
  - **Secure flag**: Cookies only transmitted over HTTPS
  - Cookie configuration: `httpOnly=True, secure=True, samesite="strict", max_age=86400`
- **Implications**:
  - JWT stored in httpOnly cookie named `access_token`
  - Backend sets cookie on successful login
  - Frontend automatically includes cookie in requests (no manual token management)
  - Logout endpoint clears cookie: `response.delete_cookie("access_token")`

### Input Validation with Pydantic
- **Context**: Prevent SQL injection, XSS, and other injection attacks
- **Sources Consulted**:
  - Pydantic documentation (validators, custom validation)
  - FastAPI request validation
  - OWASP Input Validation guidelines
- **Findings**:
  - Pydantic schemas validate all request bodies automatically
  - Custom validators: `@validator('email')` for format validation
  - String sanitization: `str.strip()` for whitespace, HTML escaping for user-generated content
  - SQLAlchemy ORM uses parameterized queries (prevents SQL injection)
  - Pydantic rejects unexpected fields by default (`extra="forbid"`)
- **Implications**:
  - Define Pydantic schemas for all request/response models
  - Custom validators for email, password strength, country codes
  - No manual SQL query construction (ORM only)

## Architecture Pattern Evaluation

| Option | Description | Strengths | Risks / Limitations | Notes |
|--------|-------------|-----------|---------------------|-------|
| **Middleware-based (Selected)** | Authentication/authorization via FastAPI middleware and dependencies | Clean separation, reusable dependencies, Pythonic | Middleware order matters | Aligns with FastAPI best practices |
| Decorator-based | Custom decorators for route protection | Familiar pattern, explicit | Not FastAPI idiomatic, harder to test | Less integration with FastAPI DI |
| Manual checks | Per-route authentication logic | Simple for small apps | Code duplication, error-prone | Does not scale |

**Selected**: Middleware-based with Dependency Injection
- FastAPI dependency injection provides clean, testable authentication
- Reusable dependencies: `get_current_user`, `require_role(role)`
- Middleware for global concerns: rate limiting, CORS, CSRF
- Follows FastAPI community best practices

## Design Decisions

### Decision: JWT Token Storage (httpOnly Cookies)
- **Context**: Need secure token storage that prevents XSS attacks
- **Alternatives Considered**:
  1. **LocalStorage** - Simple but vulnerable to XSS
  2. **httpOnly Cookies** - XSS-safe, requires CSRF protection
  3. **Memory-only storage** - Most secure but loses on page refresh
- **Selected Approach**: httpOnly Cookies with SameSite=Strict
  - Backend sets cookie on login: `response.set_cookie("access_token", token, httpOnly=True, secure=True, samesite="strict")`
  - Frontend automatically includes cookie in requests
  - CSRF protection via double-submit cookie pattern
- **Rationale**:
  - httpOnly flag prevents JavaScript access (XSS protection)
  - SameSite=Strict prevents CSRF attacks
  - Automatic cookie handling reduces frontend complexity
- **Trade-offs**:
  - **Benefit**: Strong XSS protection
  - **Compromise**: Requires CSRF token implementation
  - **Compromise**: CORS configuration more complex
- **Follow-up**: Verify CSRF token validation in integration tests

### Decision: Rate Limiting Backend (In-Memory for MVP, Redis for Production)
- **Context**: Requirements specify rate limiting (100/1000 req/min), need scalable solution
- **Alternatives Considered**:
  1. **In-memory backend** - Simple, no dependencies, single-instance only
  2. **Redis backend** - Distributed, scalable, additional infrastructure
  3. **Database-backed** - Persistent but slow
- **Selected Approach**: In-memory for MVP, Redis for production scaling
  - MVP: slowapi with in-memory backend
  - Production: slowapi with Redis backend (horizontal scaling)
- **Rationale**:
  - MVP likely single-instance deployment (in-memory sufficient)
  - Redis required only when horizontal scaling needed
  - slowapi supports both backends (easy migration)
- **Trade-offs**:
  - **Benefit**: MVP simplicity (no Redis dependency)
  - **Compromise**: Single-instance limitation for MVP
- **Follow-up**: Document Redis migration path in deployment guide

### Decision: Password Strength Validation
- **Context**: Requirements specify minimum 8 characters with complexity rules
- **Alternatives Considered**:
  1. **Regex validation** - Fast but brittle
  2. **Custom Pydantic validator** - Flexible, clear error messages
  3. **Third-party library (passlib)** - Overkill for simple validation
- **Selected Approach**: Custom Pydantic validator
  ```python
  @validator('password')
  def validate_password_strength(cls, v):
      if len(v) < 8:
          raise ValueError('Password must be at least 8 characters')
      if not re.search(r'[A-Z]', v):
          raise ValueError('Password must contain uppercase letter')
      if not re.search(r'[a-z]', v):
          raise ValueError('Password must contain lowercase letter')
      if not re.search(r'\d', v):
          raise ValueError('Password must contain digit')
      if not re.search(r'[!@#$%^&*]', v):
          raise ValueError('Password must contain special character')
      return v
  ```
- **Rationale**:
  - Clear, maintainable validation logic
  - Pydantic integration provides automatic error handling
  - Explicit error messages improve user experience
- **Trade-offs**:
  - **Benefit**: Clear error messages per rule
  - **Compromise**: More verbose than regex
- **Follow-up**: Unit test all password validation scenarios

### Decision: Role-Based Access Control Implementation
- **Context**: Requirements specify 4 roles (guest, user, artist, admin) with different permissions
- **Alternatives Considered**:
  1. **Enum-based roles** - Simple, type-safe
  2. **Permission-based ACL** - Flexible but complex
  3. **Decorator-based** - Not FastAPI idiomatic
- **Selected Approach**: Enum-based roles with custom dependency
  ```python
  class UserRole(str, Enum):
      GUEST = "guest"
      USER = "user"
      ARTIST = "artist"
      ADMIN = "admin"
  
  def require_role(*allowed_roles: UserRole):
      async def role_checker(current_user: User = Depends(get_current_user)):
          if current_user.role not in allowed_roles:
              raise HTTPException(status_code=403, detail="Insufficient permissions")
          return current_user
      return role_checker
  ```
- **Rationale**:
  - Enum provides type safety and IDE autocomplete
  - Custom dependency integrates with FastAPI DI
  - Easy to test and reuse across routes
- **Trade-offs**:
  - **Benefit**: Type-safe, Pythonic
  - **Compromise**: Less flexible than permission-based ACL
- **Follow-up**: Document role hierarchy in design.md

## Risks & Mitigations

### Risk 1: JWT Secret Exposure
- **Description**: JWT_SECRET environment variable compromise allows token forgery
- **Impact**: Attacker can generate valid tokens, impersonate any user
- **Mitigation**:
  - Store JWT_SECRET in secure environment variable management (Vault, AWS Secrets Manager)
  - Rotate JWT_SECRET every 90 days (invalidates all tokens)
  - Never commit secrets to version control (use .env.example with placeholder)
  - Implement secret rotation strategy for production

### Risk 2: bcrypt Performance Impact on Login
- **Description**: Cost factor 12 takes ~250ms, may feel slow on high-concurrency logins
- **Impact**: User perceives slow login experience
- **Mitigation**:
  - Acceptable for MVP (cost factor 12 is industry standard)
  - Monitor login latency metrics
  - Consider async bcrypt library (bcrypt is synchronous, blocks event loop)
  - Future: Implement Redis caching for frequently accessed users (with TTL)

### Risk 3: Rate Limiting Bypass via Distributed IPs
- **Description**: Attackers can bypass IP-based rate limiting using VPN/proxy rotation
- **Impact**: Brute force attacks still possible
- **Mitigation**:
  - Implement account lockout after 5 failed attempts (Requirement 13)
  - Monitor failed login attempts per user (not just IP)
  - CAPTCHA after 3 failed attempts (future enhancement)
  - Notification email on suspicious activity

### Risk 4: CSRF Token Implementation Complexity
- **Description**: CSRF protection adds frontend/backend coordination complexity
- **Impact**: Development overhead, potential bugs
- **Mitigation**:
  - Clear documentation for frontend team (cookie reading, header setting)
  - Provide example Axios interceptor for CSRF token
  - Integration tests verify CSRF protection
  - Fallback: Accept temporary CSRF vulnerability for MVP, fix before production

## References

### Official Documentation
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/) - OAuth2, JWT, dependencies
- [python-jose](https://python-jose.readthedocs.io/) - JWT library
- [bcrypt](https://github.com/pyca/bcrypt/) - Password hashing
- [slowapi](https://slowapi.readthedocs.io/) - Rate limiting for FastAPI
- [Pydantic Validators](https://docs.pydantic.dev/latest/concepts/validators/) - Custom validation

### Security Resources
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP CSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)
- [JWT Best Practices](https://datatracker.ietf.org/doc/html/rfc8725)

### Internal References
- `.sdd/steering/tech.md` - Technology stack, TDD requirements
- `.sdd/steering/structure.md` - Backend structure patterns
