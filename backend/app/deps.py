"""
FastAPI Dependencies: DB-Session, aktueller Benutzer, Rollen-Guards.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, UserRole
from app.security import decode_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ungueltige oder abgelaufene Anmeldedaten",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except ValueError:
        raise credentials_exception

    user = db.query(User).filter(User.username == username).first()
    if user is None or not user.is_active:
        raise credentials_exception
    return user


def require_role(*roles: UserRole):
    """Dependency-Factory fuer rollenbasierte Zugriffskontrolle."""

    def checker(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Keine ausreichenden Berechtigungen fuer diese Aktion",
            )
        return user

    return checker


require_admin = require_role(UserRole.ADMIN)
require_operator = require_role(UserRole.ADMIN, UserRole.OPERATOR)
require_viewer = require_role(UserRole.ADMIN, UserRole.OPERATOR, UserRole.VIEWER)
