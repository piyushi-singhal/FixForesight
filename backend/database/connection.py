import os
print("[connection] import os done")
from sqlalchemy import create_engine
print("[connection] import create_engine done")
from sqlalchemy.orm import declarative_base, sessionmaker
print("[connection] import declarative_base/sessionmaker done")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/pdm_db")
print(f"[connection] DATABASE_URL is: {DATABASE_URL}")

# Fallback to SQLite if Postgres is unavailable
try:
    print("[connection] creating engine...")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)
    print("[connection] engine created, testing connection...")
    # Test connection
    conn = engine.connect()
    print("[connection] conn.connect() succeeded")
    conn.close()
    print("✓ Successfully connected to PostgreSQL")
except Exception as e:
    print(f"[connection] conn.connect() failed: {e}")
    db_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "pdm_db.db")
    print(f"[connection] using sqlite file: {db_file}")
    print(f"Warning: PostgreSQL connection failed ({e}). Falling back to local SQLite: {db_file}")
    DATABASE_URL = f"sqlite:///{db_file}"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
    print("[connection] SQLite engine created")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
print("[connection] SessionLocal created")
Base = declarative_base()

def get_db():
    db_session = SessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
