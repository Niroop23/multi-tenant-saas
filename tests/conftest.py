import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database.base import Base
from app.database.session import get_db
from app.core.config import settings


SQLALCHEMY_DATABASE_URL = settings.TEST_DATABASE_URL

engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal= sessionmaker(bind=engine, autocommit=False,autoflush=False)


@pytest.fixture(scope="session",autouse=True)
def db_Setup():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    
    
@pytest.fixture()
def db():
    db= TestingSessionLocal()
    
    try:
        yield db
    finally:
        db.close()
        
        
@pytest.fixture()
def client(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


def register_login(client,email,username,password):
    res=client.post("/auth/register", json={"email":email,
                                      "username":username,
                                      "password":password})
    assert res.status_code== 200
    
    res=client.post("/auth/login",json={
        "identifier":email,
        "password":password} )
    
    assert res.status_code ==200
    
    return res.json()["access_token"]