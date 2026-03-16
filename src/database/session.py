from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./rag_system.db")

if "sqlite" in DATABASE_URL:
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database - create all tables"""
    print("🔄 Initializing database...")
    try:
        # Import ALL models FIRST to register them with Base
        from src.database.models import User, Organization, APIKey, AuditLog

        print(f"📦 Models imported: User, Organization, APIKey, AuditLog")
        print(f"📊 Base.metadata.tables: {list(Base.metadata.tables.keys())}")

        # Create all tables
        Base.metadata.create_all(bind=engine)

        print("✅ Database initialized successfully!")
        print(f"📊 Tables created: {engine.table_names() if hasattr(engine, 'table_names') else 'check db'}")
        return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        import traceback
        traceback.print_exc()
        raise