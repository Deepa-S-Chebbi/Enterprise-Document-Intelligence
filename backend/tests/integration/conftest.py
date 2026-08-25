import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
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
# Database safety check
# ------------------------------------------------------------------

@pytest.fixture(scope="session", autouse=True)
def verify_test_database():
    with engine.connect() as connection:
        database_name = connection.execute(
            text("SELECT current_database()")
        ).scalar()

    assert database_name == "document_intelligence_test", (
        f"Integration tests connected to unexpected database: "
        f"{database_name}"
    )


# ------------------------------------------------------------------
# Database cleanup
# ------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_database():
    """
    Clean test data before and after every integration test.
    """

    with TestingSessionLocal() as session:
        session.execute(
            text(
                """
                TRUNCATE TABLE
                    extraction_results,
                    ocr_results,
                    documents
                RESTART IDENTITY CASCADE
                """
            )
        )
        session.commit()

    yield

    with TestingSessionLocal() as session:
        session.execute(
            text(
                """
                TRUNCATE TABLE
                    extraction_results,
                    ocr_results,
                    documents
                RESTART IDENTITY CASCADE
                """
            )
        )
        session.commit()


# ------------------------------------------------------------------
# Database session fixture
# ------------------------------------------------------------------

@pytest.fixture
def db_session():
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