
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.database import SessionLocal
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.schemas.user import UserCreate, UserResponse, Token

from app.core.security import (
    hash_password,
    authenticate_user,
    create_access_token,
    get_current_user
)

from app.services.password_reset_service import (
    create_password_reset_token,
    get_valid_reset_token
)

from app.email_service import send_email


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


# Request Schemas
class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(min_length=8)


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# REGISTER
@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(User).filter(
        User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    new_user = User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


# LOGIN
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = authenticate_user(
        form_data.username,
        form_data.password,
        db
    )

    if not db_user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    access_token = create_access_token(
        {"sub": db_user.email}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# FORGOT PASSWORD
@router.post("/forgot-password")
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    # Same response whether email exists or not
    if not user:
        return {
            "message": "If this email is registered, a password reset link will be sent."
        }

    try:
        raw_token = create_password_reset_token(
            db,
            user.id
        )

        reset_link = (
            "http://localhost:8501/?reset_token="
            + raw_token
        )

        email_body = f"""
Hello {user.username},

We received a request to reset your password.

Click the link below to reset your password:

{reset_link}

This link expires in 15 minutes.

If you did not request this, please ignore this email.

Regards,
Financial Portfolio Recommendation Engine
"""

        send_email(
            to_email=user.email,
            subject="Password Reset Request",
            body=email_body
        )

    except Exception:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Unable to process password reset request. Please try again later."
        )

    return {
        "message": "If this email is registered, a password reset link will be sent."
    }


# RESET PASSWORD
@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    reset_record = get_valid_reset_token(
        db,
        request.token
    )

    if not reset_record:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset link."
        )

    user = db.query(User).filter(
        User.id == reset_record.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired password reset link."
        )

    user.password = hash_password(request.new_password)

    reset_record.used = True

    db.commit()

    return {
        "message": "Password reset successful. Please log in with your new password."
    }


# PROFILE
@router.get("/me", response_model=UserResponse)
def get_my_profile(
    current_user: User = Depends(get_current_user)
):
    return current_user
