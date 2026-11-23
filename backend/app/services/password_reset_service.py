
import secrets
import hashlib
from datetime import datetime, timedelta

from sqlalchemy.orm import Session

from app.models.password_reset_token import PasswordResetToken


def hash_reset_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def create_password_reset_token(db: Session, user_id: int):
    # Invalidate previous unused tokens
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user_id,
        PasswordResetToken.used == False
    ).update({"used": True})

    # Generate a secure random token
    raw_token = secrets.token_urlsafe(32)

    # Store only the hashed token
    token_hash = hash_reset_token(raw_token)

    reset_record = PasswordResetToken(
        user_id=user_id,
        token_hash=token_hash,
        expires_at=datetime.utcnow() + timedelta(minutes=15),
        used=False
    )

    db.add(reset_record)
    db.commit()

    return raw_token


def get_valid_reset_token(db: Session, raw_token: str):
    token_hash = hash_reset_token(raw_token)

    reset_record = db.query(PasswordResetToken).filter(
        PasswordResetToken.token_hash == token_hash,
        PasswordResetToken.used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()

    return reset_record
