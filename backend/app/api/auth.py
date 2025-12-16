"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user
from app.schemas.auth import Token, LoginRequest, RegisterRequest, RefreshTokenRequest
from app.schemas.user import UserResponse
from app.services.auth import AuthService
from app.services.user import UserService
from app.services.audit import AuditService
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(
    request: Request,
    user_data: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    # Check if email already exists
    existing_user = UserService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )

    # Create user
    from app.schemas.user import UserCreate
    user_create = UserCreate(
        email=user_data.email,
        password=user_data.password,
        display_name=user_data.display_name,
        has_adhd=user_data.has_adhd,
        has_autism_spectrum=user_data.has_autism_spectrum,
        has_anxiety=user_data.has_anxiety,
        has_depression=user_data.has_depression
    )
    user = UserService.create_user(db, user_create)

    # Log registration
    AuditService.log_action(
        db=db,
        action_type="USER_REGISTERED",
        user_id=user.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent")
    )

    return user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Authenticate user and return tokens"""
    user = AuthService.authenticate_user(db, login_data.email, login_data.password)

    if not user:
        # Log failed attempt
        existing_user = UserService.get_user_by_email(db, login_data.email)
        if existing_user:
            AuditService.log_user_login(
                db=db,
                user_id=existing_user.id,
                ip_address=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
                success=False
            )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Check MFA if enabled
    if user.mfa_enabled and not login_data.mfa_code:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="MFA code required"
        )

    # Log successful login
    AuditService.log_user_login(
        db=db,
        user_id=user.id,
        ip_address=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown"),
        success=True
    )

    return AuthService.create_tokens(user)


@router.post("/refresh", response_model=Token)
def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    token_data = AuthService.verify_token(refresh_data.refresh_token)
    if not token_data or not token_data.user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    return AuthService.create_tokens(user)


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard tokens)"""
    # In production, would add token to blacklist in Redis
    return {"message": "Successfully logged out"}
