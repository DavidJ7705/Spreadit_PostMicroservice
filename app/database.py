import os
from dotenv import load_dotenv

from sqlalchemy import create_engine, event
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker


# Pick env file by APP_ENV (default dev)
envfile = {
    "dev": ".env.dev",  #development enviromnet
    "docker": ".env.docker", #docker enviromnet
    "test": ".env.test", #testing enviromnet
}.get(os.getenv("APP_ENV", "dev"), ".env.dev")

# Load environment variables from the selected file
load_dotenv(envfile, override=True)


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./app.db")
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true" # enable sql echo with env varl loggin if its true
RETRIES = int(os.getenv("DB_RETRIES", "10"))
DELAY = float(os.getenv("DB_RETRY_DELAY", "1.5"))

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# small retry (harmless for SQLite, useful for Postgres)
for _ in range(RETRIES):
    try:
        # create the SQLAlchemy engine
        engine = create_engine(DATABASE_URL, pool_pre_ping=True, echo=SQL_ECHO, connect_args=connect_args)
        with engine.connect():  # smoke test connection
            pass
        break
    except OperationalError:
        time.sleep(DELAY)

#enables foreign keys for sqlite
if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def enable_foreign_keys(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, expire_on_commit=False)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
