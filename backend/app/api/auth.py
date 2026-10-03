"""Authentication endpoints — register, login, refresh."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_password_change_user
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.auth import (
    ChangePasswordRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth import hash_password, verify_password
from app.services.jwt import (
    create_access_token,
    create_password_change_token,
    create_refresh_token,
    decode_token,
)

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    # Check if phone already exists
    existing = db.query(User).filter(User.phone == request.phone).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Phone number already registered",
        )

    # Create user
    user = User(
        name=request.name,
        phone=request.phone,
        email=request.email,
        role=UserRole.FARMER,
        hashed_password=hash_password(request.password),
        is_active=True,
        language_preference=request.language_preference,
        consent_given=request.consent_given,
        consent_date=datetime.now(timezone.utc) if request.consent_given else None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Generate tokens
    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return JWT tokens."""
    user = db.query(User).filter(User.phone == request.phone).first()

    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect phone number or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated",
        )

    if user.password_change_required:
        return TokenResponse(
            access_token=create_password_change_token(user.id),
            password_change_required=True,
        )

    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/change-password", response_model=TokenResponse)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_password_change_user),
    db: Session = Depends(get_db),
):
    """Require the current password, then replace it before granting a normal session."""
    if not verify_password(request.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    if request.current_password == request.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must differ from the current password",
        )

    current_user.hashed_password = hash_password(request.new_password)
    current_user.password_change_required = False
    db.add(current_user)
    db.commit()
    db.refresh(current_user)

    return TokenResponse(
        access_token=create_access_token(current_user.id, current_user.role.value),
        refresh_token=create_refresh_token(current_user.id),
        password_change_required=False,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(request: RefreshRequest, db: Session = Depends(get_db)):
    """Get new access token using refresh token."""
    payload = decode_token(request.refresh_token)

    if payload is None or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    from uuid import UUID

    user = db.query(User).filter(User.id == UUID(payload["sub"])).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    if user.password_change_required:
        return TokenResponse(
            access_token=create_password_change_token(user.id),
            password_change_required=True,
        )

    access_token = create_access_token(user.id, user.role.value)
    refresh_token = create_refresh_token(user.id)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user's profile."""
    return UserResponse(
        id=str(current_user.id),
        name=current_user.name,
        phone=current_user.phone,
        email=current_user.email,
        role=current_user.role.value,
        language_preference=current_user.language_preference,
        is_active=current_user.is_active,
        password_change_required=current_user.password_change_required,
    )
