from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Integer, Text, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from .session import Base


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False)
    owner_id = Column(String(36), nullable=True)
    subscription_tier = Column(String(50), default="starter")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # One-to-many: Organization has MANY Users
    users = relationship("User", back_populates="organization")
    api_keys = relationship("APIKey", back_populates="organization")
    audit_logs = relationship("AuditLog", back_populates="organization")


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50), default="viewer")
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    # Many-to-one: User belongs to ONE Organization
    organization = relationship("Organization", back_populates="users")
    api_keys = relationship("APIKey", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user")


class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    key_hash = Column(String(255), unique=True, nullable=False)
    name = Column(String(255))
    is_active = Column(Boolean, default=True)
    last_used = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="api_keys")
    organization = relationship("Organization", back_populates="api_keys")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100))
    resource_id = Column(String(255))
    details = Column(Text)
    ip_address = Column(String(45), nullable=True)
    status = Column(String(20), default="success")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

    user = relationship("User", back_populates="audit_logs")
    organization = relationship("Organization", back_populates="audit_logs")

    __table_args__ = (
        Index('idx_org_date', 'organization_id', 'created_at'),
    )