"""
Authentication Routes - Task 3.2, 5.1, 5.2
User registration and login endpoints
Requirements: 1.1-1.8, 2.1-2.7
"""
from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from app.database import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, UserResponse
from app.services.user_service import UserService
from app.services.password_service import PasswordService
from app.services.auth_service import AuthService
from app.repositories.user_repository import UserRepository
from app.dependencies.auth import get_current_user
from app.dependencies.rbac import require_role
from app.models.user import User
from app.middleware.rate_limit import limiter

router = APIRouter(prefix="/api/v1/auth", tags=["authentication"])


def get_user_service(db: AsyncSession = Depends(get_db)) -> UserService:
    """
    Dependency to create UserService with required dependencies

    Args:
        db: Database session from FastAPI dependency

    Returns:
        UserService: Configured user service instance
    """
    password_service = PasswordService()
    user_repository = UserRepository(db)
    return UserService(password_service, user_repository)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user",
    description="Create new user account with email and password"
)
@limiter.limit("10/minute")  # Stricter limit for registration
async def register_user(
    register_request: RegisterRequest,
    request: Request,
    user_service: UserService = Depends(get_user_service)
):
    """
    Register new user endpoint

    Requirements:
    - 1.1: Validate email format (Pydantic EmailStr)
    - 1.2: Validate password strength (Pydantic validator)
    - 1.3: Hash password with bcrypt
    - 1.4: Set default 'user' role
    - 1.5: Return user details (id, email, role, timestamps)
    - 1.6: Check for duplicate emails
    - 1.7: Return detailed validation errors
    - 1.8: Never expose password_hash

    Args:
        request: RegisterRequest with email and password
        user_service: UserService dependency

    Returns:
        UserResponse: Created user data (excludes password_hash)

    Raises:
        HTTPException 409: Email already registered
        HTTPException 422: Validation error (handled by Pydantic)
    """
    try:
        # Register user (validation happens in service layer)
        user = await user_service.register_user(
            email=register_request.email,
            password=register_request.password
        )

        # Return user response (UserResponse excludes password_hash)
        return UserResponse(
            id=user.id,
            email=user.email,
            role=user.role,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

    except ValueError as e:
        error_message = str(e)

        # Handle duplicate email error
        if "already registered" in error_message.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=error_message
            )

        # Handle other validation errors
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=error_message
        )


@router.post(
    "/login",
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return JWT token"
)
@limiter.limit("5/minute")  # Strict limit for login attempts
async def login(
    response: Response,
    login_request: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    User login endpoint

    Requirements:
    - 2.1: Validate credentials against database
    - 2.2: Generate JWT token on successful login
    - 2.3: Include user data in token payload
    - 2.4: Set token expiration
    - 2.5: Return 401 for invalid credentials
    - 2.6: Generic error message (don't reveal if email exists)
    - 2.7: Set httpOnly cookie with secure flags

    Args:
        response: FastAPI Response object for setting cookies
        request: LoginRequest with email and password
        db: Database session

    Returns:
        dict: access_token in response body

    Raises:
        HTTPException 401: Invalid credentials
        HTTPException 422: Validation error (handled by Pydantic)
    """
    # Initialize services
    password_service = PasswordService()
    auth_service = AuthService()
    user_repository = UserRepository(db)

    try:
        # Look up user by email
        user = await user_repository.get_user_by_email(login_request.email)

        # Check if user exists and password is correct
        if user is None:
            # User not found - return generic error
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Verify password
        password_valid = password_service.verify_password(
            login_request.password,
            user.password_hash
        )

        if not password_valid:
            # Wrong password - return generic error (same as user not found)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials"
            )

        # Generate JWT token
        token = auth_service.generate_token(
            user_id=user.id,
            email=user.email,
            role=user.role
        )

        # Set httpOnly cookie with secure flags
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,      # Prevent JavaScript access
            secure=True,        # HTTPS only (in production)
            samesite="none",    # Allow cross-site cookies (required for different domains)
            max_age=86400       # 24 hours (same as token expiration)
        )

        # Return token in response body as well
        return {"access_token": token}

    except HTTPException:
        # Re-raise HTTP exceptions (401)
        raise

    except Exception as e:
        # Catch any other errors and return generic error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user",
    description="Get authenticated user profile (protected route)"
)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user profile

    Protected route that requires valid JWT token in cookie.

    Requirements:
    - 4.1: Extract token from cookie
    - 4.2: Validate token
    - 4.3: Return user data

    Args:
        current_user: Current user from get_current_user dependency

    Returns:
        UserResponse: Current user profile
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        role=current_user.role,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )


@router.post(
    "/logout",
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Logout user and clear authentication cookie"
)
async def logout(response: Response):
    """
    Logout user endpoint

    Clears the authentication cookie (httpOnly JWT cookie)

    Returns:
        200 OK with success message
    """
    # Clear the access_token cookie by setting it to empty with max_age=0
    response.delete_cookie(
        key="access_token",
        httponly=True,
        secure=True,
        samesite="strict"
    )

    return {"message": "Successfully logged out"}


@router.get(
    "/admin-only",
    summary="Admin only endpoint (test)",
    description="Test endpoint that requires admin role"
)
async def admin_only(current_user: User = Depends(require_role("admin"))):
    """
    Test endpoint that requires admin role

    Requirements:
    - Role-based access control
    - Only admin users can access

    Args:
        current_user: Current user with admin role

    Returns:
        dict: Success message
    """
    return {
        "message": "Admin access granted",
        "user": current_user.email,
        "role": current_user.role
    }


@router.get(
    "/export-data",
    summary="Export user data (GDPR)",
    description="Export all user personal data for GDPR compliance"
)
async def export_user_data(current_user: User = Depends(get_current_user)):
    """
    Export user data endpoint - GDPR Task 13.1

    Requirements:
    - 11.1: Return all user personal data
    - 11.4: JSON format

    Args:
        current_user: Authenticated user

    Returns:
        dict: All user personal data
    """
    return {
        "user_id": current_user.id,
        "email": current_user.email,
        "role": current_user.role,
        "created_at": current_user.created_at.isoformat() if current_user.created_at else None,
        "updated_at": current_user.updated_at.isoformat() if current_user.updated_at else None,
        "account_status": "locked" if current_user.is_locked else "active",
        "failed_login_attempts": current_user.failed_login_attempts,
        # Note: In full implementation, would include related data:
        # - playlists, reviews, listening history, etc.
        "message": "This is your complete personal data. In full system, this would include playlists, reviews, etc."
    }


@router.delete(
    "/delete-account",
    summary="Delete user account (GDPR)",
    description="Permanently delete user account and personal data"
)
async def delete_user_account(
    password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user account endpoint - GDPR Task 13.2

    Requirements:
    - 11.2: Delete user account
    - 11.3: Anonymize related data
    - 11.5: Require password confirmation

    Args:
        password: User password for confirmation
        current_user: Authenticated user
        db: Database session

    Returns:
        dict: Confirmation message
    """
    # Verify password
    password_service = PasswordService()
    if not password_service.verify_password(password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid password"
        )

    # Delete user (in full implementation, would anonymize related data)
    user_repository = UserRepository(db)

    # Log deletion in audit log (Task 14)
    # In full implementation: log to auth_audit_log

    # Delete user from database
    from sqlalchemy import delete
    await db.execute(delete(User).where(User.id == current_user.id))
    await db.commit()

    return {
        "message": "Account successfully deleted",
        "email": current_user.email,
        "deletion_time": datetime.utcnow().isoformat()
    }
