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
    # Cleanup - close connection (this will be handled by the test teardown)


@pytest.mark.asyncio
async def test_execute_insert(db):
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


@pytest.mark.asyncio
async def test_execute_insert_in_memory(in_memory_db):
    try:
        # Create test table first
        await in_memory_db.execute(
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
        await in_memory_db.execute(
            "INSERT INTO test_table (name, value) VALUES (?, ?)", ("test_name", 123)
        )

        # Verify insertion
        rows = await in_memory_db.query(
            "SELECT * FROM test_table WHERE name = ?", ("test_name",)
        )

        assert len(rows) == 1
        assert rows[0]["name"] == "test_name"
        assert rows[0]["value"] == 123
    finally:
        await in_memory_db.close()


@pytest.mark.asyncio
async def test_query_multiple_rows(db):
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


@pytest.mark.asyncio
async def test_query_multiple_rows_in_memory(in_memory_db):
    try:
        # Create test table first
        await in_memory_db.execute(
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
            await in_memory_db.execute(
                "INSERT INTO test_table (name, value) VALUES (?, ?)", (name, value)
            )

        # Query with filter
        rows = await in_memory_db.query(
            "SELECT * FROM test_table WHERE value > ?", (1,)
        )

        assert len(rows) == 2
        assert rows[0]["name"] == "name2"
        assert rows[1]["name"] == "name3"
    finally:
        await in_memory_db.close()


@pytest.mark.asyncio
async def test_query_no_results(db):
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
    rows = await db.query("SELECT * FROM test_table WHERE name = ?", ("nonexistent",))

    assert len(rows) == 0


@pytest.mark.asyncio
async def test_query_no_results_in_memory(in_memory_db):
    try:
        # Create test table first
        await in_memory_db.execute(
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
        rows = await in_memory_db.query(
            "SELECT * FROM test_table WHERE name = ?", ("nonexistent",)
        )

        assert len(rows) == 0
    finally:
        await in_memory_db.close()


@pytest.mark.asyncio
async def test_invalid_query(db):
    # Test invalid SQL syntax
    with pytest.raises(Exception):
        await db.execute("INVALID SQL QUERY", ())


@pytest.mark.asyncio
async def test_invalid_query_in_memory(in_memory_db):
    # Test invalid SQL syntax
    with pytest.raises(Exception):
        await in_memory_db.execute("INVALID SQL QUERY", ())
