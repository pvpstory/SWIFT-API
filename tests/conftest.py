# tests/conftest.py
import sys
import os
import pytest
import pytest_asyncio
import aiosqlite
# Use TestClient from FastAPI
from fastapi.testclient import TestClient

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app, get_db_connection

TEST_DB_NAME = "test_swift_codes.db"

async def create_tables(db):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS SWIFT_CODES (
            COUNTRY_ISO2 TEXT,
            SWIFT_CODE TEXT PRIMARY KEY,
            NAME TEXT,
            ADDRESS TEXT,
            COUNTRY_NAME TEXT,
            ISHEADQUARTER TEXT
        )
    """)
    await db.commit()

async def clear_tables(db):
    await db.execute("DELETE FROM SWIFT_CODES")
    await db.commit()

@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_session():
    db = await aiosqlite.connect(TEST_DB_NAME)
    await create_tables(db)
    yield db
    await clear_tables(db)
    await db.close()

@pytest.fixture(scope="function")
def test_client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db_connection] = override_get_db

    with TestClient(app) as client:
        yield client

    app.dependency_overrides.clear()