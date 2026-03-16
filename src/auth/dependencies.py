from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from . import security
from src.database.session import get_db
from src.database import models as db_models

security_scheme = HTTPBearer()


async def get_current_user(
        credentials=Depends(security_scheme),
        db: Session = Depends(get_db)
) -> db_models.User:
    token = credentials.credentials

    try:
        token_data = security.verify_token(token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )

    user = db.query(db_models.User).filter(
        db_models.User.id == token_data.user_id
    ).first()

    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )

    return user


async def get_current_admin(
        user: db_models.User = Depends(get_current_user)
) -> db_models.User:
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user


async def get_current_editor(
        user: db_models.User = Depends(get_current_user)
) -> db_models.User:
    if user.role not in ["admin", "editor"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Editor access required"
        )
    return user