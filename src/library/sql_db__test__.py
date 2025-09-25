import pytest
import os
import tempfile
from src.library.sql_db import SqlDb


@pytest.fixture
def db():
    # Use temporary test database with unique name
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name

    # Create test database
    db = SqlDb(db_path)

    # Return the database instance
    yield db

    # Cleanup - delete test database
    try:
        os.remove(db_path)
    except FileNotFoundError:
        pass


@pytest.fixture
def in_memory_db():
    # Create in-memory database
    db = SqlDb(":memory:")
    yield db


@pytest.fixture(params=["file", "memory"])
def any_db(request, db, in_memory_db):
    if request.param == "file":
        return db
    else:
        return in_memory_db


@pytest.mark.asyncio
async def test_execute_insert(any_db):
    db = any_db
    try:
        # Create test table first
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
            """,
            (),
        )

        # Test inserting data
        await db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)", ("test_name", 123)
        )

        # Verify insertion
        rows = await db.query("SELECT * FROM test_table WHERE name = ?", ("test_name",))

        assert len(rows) == 1
        assert rows[0]["name"] == "test_name"
        assert rows[0]["value"] == 123
    finally:
        if isinstance(db, SqlDb) and db._is_in_memory:
            await db.close()


@pytest.mark.asyncio
async def test_query_multiple_rows(any_db):
    db = any_db
    try:
        # Create test table first
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
            """,
            (),
        )

        # Insert test data
        test_data = [("name1", 1), ("name2", 2), ("name3", 3)]

        for name, value in test_data:
            await db.execute(
                "INSERT INTO test_table (name, value) VALUES (?, ?)", (name, value)
            )

        # Query with filter
        rows = await db.query("SELECT * FROM test_table WHERE value > ?", (1,))

        assert len(rows) == 2
        assert rows[0]["name"] == "name2"
        assert rows[1]["name"] == "name3"
    finally:
        if isinstance(db, SqlDb) and db._is_in_memory:
            await db.close()


@pytest.mark.asyncio
async def test_query_no_results(any_db):
    db = any_db
    try:
        # Create test table first
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
            """,
            (),
        )

        # Query empty table
        rows = await db.query(
            "SELECT * FROM test_table WHERE name = ?", ("nonexistent",)
        )

        assert len(rows) == 0
    finally:
        if isinstance(db, SqlDb) and db._is_in_memory:
            await db.close()


@pytest.mark.asyncio
async def test_invalid_query(any_db):
    db = any_db
    try:
        # Test invalid SQL syntax
        with pytest.raises(Exception):
            await db.execute("INVALID SQL QUERY", ())
    finally:
        if isinstance(db, SqlDb) and db._is_in_memory:
            await db.close()


@pytest.mark.asyncio
async def test_transaction_success(any_db):
    db = any_db
    try:
        # Create test table first
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
            """,
            (),
        )

        # Test successful transaction
        async with db.transaction() as tx:
            await tx.execute(
                "INSERT INTO test_table (name, value) VALUES (?, ?)", ("test1", 1)
            )
            await tx.execute(
                "INSERT INTO test_table (name, value) VALUES (?, ?)", ("test2", 2)
            )

        # Verify both inserts were committed
        rows = await db.query("SELECT * FROM test_table ORDER BY id")
        assert len(rows) == 2
        assert rows[0]["name"] == "test1"
        assert rows[1]["name"] == "test2"
    finally:
        if isinstance(db, SqlDb) and db._is_in_memory:
            await db.close()


@pytest.mark.asyncio
async def test_transaction_rollback_on_exception(any_db):
    db = any_db
    try:
        # Create test table first
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
            """,
            (),
        )

        # Test transaction rollback on exception
        with pytest.raises(ValueError):
            async with db.transaction() as tx:
                await tx.execute(
                    "INSERT INTO test_table (name, value) VALUES (?, ?)",
                    ("test1", 1),
                )
                raise ValueError("Simulated error")

        # Verify no data was committed
        rows = await db.query("SELECT * FROM test_table")
        assert len(rows) == 0
    finally:
        if isinstance(db, SqlDb) and db._is_in_memory:
            await db.close()


@pytest.mark.asyncio
async def test_query_in_transaction(any_db):
    db = any_db
    try:
        # Create test table first
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
            """,
            (),
        )

        # Insert test data
        await db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)", ("test1", 1)
        )
        await db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)", ("test2", 2)
        )

        # Test query within transaction
        async with db.transaction() as tx:
            rows = await tx.query("SELECT * FROM test_table WHERE value > ?", (1,))

            assert len(rows) == 1
            assert rows[0]["name"] == "test2"
            assert rows[0]["value"] == 2
    finally:
        if isinstance(db, SqlDb) and db._is_in_memory:
            await db.close()
