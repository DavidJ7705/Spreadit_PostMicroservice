import pytest 
from fastapi.testclient import TestClient 
from sqlalchemy import create_engine, event 
from sqlalchemy.orm import sessionmaker 
 
from app.main import app, get_db 
from app.models import Base, PostDB
from sqlalchemy.pool import StaticPool 
 
TEST_DB_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DB_URL, connect_args={"check_same_thread": False}, poolclass=StaticPool) 
TestingSessionLocal = sessionmaker(bind=engine, expire_on_commit=False) 
 

@event.listens_for(engine, "connect") 
def _fk_on(dbapi_conn, _): 
    dbapi_conn.execute("PRAGMA foreign_keys=ON") 

@pytest.fixture(autouse=True) 
def _schema(): 
    Base.metadata.create_all(bind=engine) 
    yield 
    Base.metadata.drop_all(bind=engine) 
 
@pytest.fixture 
def client(): 
    def override_get_db(): 
        db = TestingSessionLocal() 
        try: 
            yield db 
        finally: 
            db.close() 
    app.dependency_overrides[get_db] = override_get_db 
    with TestClient(app) as c: 
        # hand the client to the test 
        yield c 
    app.dependency_overrides.clear() 