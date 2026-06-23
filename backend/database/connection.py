import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pdm_db")

# Fallback to SQLite if Postgres is unavailable
try:
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    # Test connection
    conn = engine.connect()
    conn.close()
    print("✓ Successfully connected to PostgreSQL")
except Exception as e:
    db_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pdm_db.db")
    print(f"Warning: PostgreSQL connection failed ({e}). Falling back to local SQLite: {db_file}")
    DATABASE_URL = f"sqlite:///{db_file}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
