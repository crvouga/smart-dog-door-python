import pytest
from datetime import datetime
from typing import Dict, Any

from src.library.sql_db import SqlDb
from src.login.login_link_db import LoginLinkDb


@pytest.fixture
def sql_db() -> SqlDb:
    db = SqlDb(":memory:")
    return db


@pytest.fixture
def login_link_db(sql_db: SqlDb) -> LoginLinkDb:
    db = LoginLinkDb(sql_db)
    return db


@pytest.mark.asyncio
async def test_insert_and_find_by_token(login_link_db: LoginLinkDb) -> None:
    # Arrange
    # Set up database schema
    async with login_link_db._sql_db.transaction() as tx:
        for up_sql in login_link_db.up():
            await tx.execute(up_sql, ())

    login_link: Dict[str, Any] = {
        "login_link__id": "test-id",
        "login_link__email_address": "test@example.com",
        "login_link__token": "test-token",
        "login_link__requested_at_utc_iso": datetime.utcnow().isoformat(),
        "login_link__status": "pending",
    }

    # Act
    await login_link_db.insert(login_link)
    found = await login_link_db.find_by_token("test-token")

    # Assert
    assert found["login_link__id"] == login_link["login_link__id"]
    assert found["login_link__email_address"] == login_link["login_link__email_address"]
    assert found["login_link__token"] == login_link["login_link__token"]
    assert found["login_link__status"] == login_link["login_link__status"]


@pytest.mark.asyncio
async def test_find_by_token_not_found(login_link_db: LoginLinkDb) -> None:
    # Arrange
    # Set up database schema
    async with login_link_db._sql_db.transaction() as tx:
        for up_sql in login_link_db.up():
            await tx.execute(up_sql, ())

    # Act
    with pytest.raises(IndexError):
        await login_link_db.find_by_token("non-existent-token")
