import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.db.base import Base
from app.db.session import get_db
from app.main import app


# ------------------------------------------------------------------
# Integration test database
# ------------------------------------------------------------------

TEST_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    settings.database_url,
)

engine = create_engine(
    TEST_DATABASE_URL,
    echo=False,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


# ------------------------------------------------------------------
# Database fixture
# ------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def verify_test_database():
    """
    Verify that integration tests are connected to the
    dedicated test database.
    """

    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar()

    assert database_name == "document_intelligence_test", (
        f"Integration tests connected to unexpected database: "
        f"{database_name}"
    )


# ------------------------------------------------------------------
# Database session fixture
# ------------------------------------------------------------------

@pytest.fixture
def db_session():
    """
    Provide a database session for integration tests.
    """

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ------------------------------------------------------------------
# FastAPI client fixture
# ------------------------------------------------------------------

@pytest.fixture
def client():
    """
    Provide a FastAPI TestClient using the test database.
    """

    def override_get_db():
        db = TestingSessionLocal()

        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()