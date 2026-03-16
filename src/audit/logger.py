from sqlalchemy.orm import Session
from src.database.models import AuditLog
from datetime import datetime
import json


class AuditLogger:
    def __init__(self, db: Session):
        self.db = db

    def log(
            self,
            user_id: str,
            organization_id: str,
            action: str,
            resource_type: str,
            resource_id: str,
            details: dict = None,
            ip_address: str = None,
            status: str = "success"
    ):
        log_entry = AuditLog(
            user_id=user_id,
            organization_id=organization_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=json.dumps(details or {}),
            ip_address=ip_address,
            status=status,
            created_at=datetime.utcnow()
        )

        self.db.add(log_entry)
        self.db.commit()

        return log_entry

    def get_logs(
            self,
            organization_id: str,
            from_date: datetime = None,
            actions: list = None,
            user_id: str = None,
            limit: int = 100
    ):
        query = self.db.query(AuditLog).filter(
            AuditLog.organization_id == organization_id
        )

        if from_date:
            query = query.filter(AuditLog.created_at >= from_date)

        if actions:
            query = query.filter(AuditLog.action.in_(actions))

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)

        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()