import secrets
import hashlib
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from src.database.models import APIKey
import uuid


class APIKeyManager:
    @staticmethod
    def generate_key() -> str:
        return secrets.token_urlsafe(32)

    @staticmethod
    def hash_key(key: str) -> str:
        return hashlib.sha256(key.encode()).hexdigest()

    @staticmethod
    def create_api_key(
            db: Session,
            user_id: str,
            organization_id: str,
            name: str,
            expires_in: str = "never"
    ) -> dict:
        key = APIKeyManager.generate_key()
        key_hash = APIKeyManager.hash_key(key)

        expires_at = None
        if expires_in != "never":
            days_map = {"7 days": 7, "30 days": 30, "90 days": 90}
            days = days_map.get(expires_in, 30)
            expires_at = datetime.utcnow() + timedelta(days=days)

        api_key = APIKey(
            id=uuid.uuid4(),
            user_id=user_id,
            organization_id=organization_id,
            key_hash=key_hash,
            name=name,
            is_active=True,
            expires_at=expires_at
        )
        db.add(api_key)
        db.commit()

        return {
            "id": str(api_key.id),
            "key": key,
            "name": name,
            "expires_at": expires_at
        }

    @staticmethod
    def verify_api_key(db: Session, key: str) -> dict:
        key_hash = APIKeyManager.hash_key(key)
        api_key = db.query(APIKey).filter(
            APIKey.key_hash == key_hash,
            APIKey.is_active == True
        ).first()

        if not api_key:
            return None

        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return None

        api_key.last_used = datetime.utcnow()
        db.commit()

        return {
            "user_id": str(api_key.user_id),
            "organization_id": str(api_key.organization_id)
        }