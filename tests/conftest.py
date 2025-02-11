import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.main import app
from src.db.models import Base
from src.core.config import settings
from src.db.session import get_db


@pytest.fixture(scope="session")
def test_db():
    """Create test database and tables"""
    test_engine = create_engine(settings.TEST_DATABASE_URL)
    TestingSessionLocal = sessionmaker(bind=test_engine)

    Base.metadata.create_all(bind=test_engine)

    yield TestingSessionLocal

    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(test_db):
    """Create test client with database session"""
    def override_get_db():
        try:
            db = test_db()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client
