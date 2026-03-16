from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from . import models as pydantic_models, security
from .dependencies import get_current_user
from src.database.session import get_db
from src.database import models as db_models
from src.audit.logger import AuditLogger

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", response_model=dict)
async def register(
        user: pydantic_models.UserRegister,
        db: Session = Depends(get_db),
        request: Request = None
):
    existing_user = db.query(db_models.User).filter(
        (db_models.User.email == user.email) |
        (db_models.User.username == user.username)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or username already registered"
        )

    hashed_pwd = security.hash_password(user.password)
    new_user = db_models.User(
        email=user.email,
        username=user.username,
        hashed_password=hashed_pwd,
        full_name=user.full_name,
        role="admin"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    org = db_models.Organization(
        name=f"{user.full_name}'s Organization",
        owner_id=new_user.id
    )
    db.add(org)
    db.commit()
    db.refresh(org)

    new_user.organization_id = org.id
    db.commit()

    return {
        "user_id": str(new_user.id),
        "email": new_user.email,
        "message": "User registered successfully"
    }


@router.post("/login", response_model=pydantic_models.TokenResponse)
async def login(
        credentials: pydantic_models.UserLogin,
        db: Session = Depends(get_db)
):
    user = db.query(db_models.User).filter(
        db_models.User.email == credentials.email
    ).first()

    if not user or not security.verify_password(
            credentials.password,
            user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    access_token = security.create_access_token(
        user_id=str(user.id),
        email=user.email,
        org_id=str(user.organization_id),
        role=user.role
    )
    refresh_token = security.create_refresh_token(user_id=str(user.id))

    user.last_login = datetime.utcnow()
    db.commit()

    return pydantic_models.TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token
    )


@router.post("/refresh", response_model=pydantic_models.TokenResponse)
async def refresh_token(
        refresh_token: str,
        db: Session = Depends(get_db)
):
    try:
        payload = security.jwt.decode(
            refresh_token,
            security.SECRET_KEY,
            algorithms=[security.ALGORITHM]
        )
        user_id = payload.get("user_id")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        user = db.query(db_models.User).filter(
            db_models.User.id == user_id
        ).first()

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        access_token = security.create_access_token(
            user_id=str(user.id),
            email=user.email,
            org_id=str(user.organization_id),
            role=user.role
        )

        return pydantic_models.TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.get("/me", response_model=pydantic_models.UserResponse)
async def get_current_user_info(
        current_user: db_models.User = Depends(get_current_user)
):
    return current_user