import aiosqlite
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional, AsyncGenerator
from abc import ABC, abstractmethod


class ISqlDb(ABC):
    """Abstract interface for database operations.

    This interface allows code to be agnostic to whether it's working
    with a regular database connection or a transaction.
    """

    @abstractmethod
    async def execute(self, query: str, params: tuple) -> None:
        """Execute a SQL query that modifies the database.

        Args:
            query: SQL query string with ? placeholders
            params: Tuple of parameter values to insert into query
        """
        pass

    @abstractmethod
    async def query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SQL query that retrieves data.

        Args:
            query: SQL query string with ? placeholders
            params: Tuple of parameter values to insert into query

        Returns:
            List of dictionaries representing database rows
        """
        pass


class SqlDb(ISqlDb):
    """A simple async SQLite database wrapper.

    Example:
        db = SqlDb("path/to/database.db")

        # Insert data
        await db.execute(
            "INSERT INTO users (name, age) VALUES (?, ?)",
            ("Alice", 30)
        )

        # Query data
        rows = await db.query(
            "SELECT * FROM users WHERE age > ?",
            (25,)
        )

        # Use transactions for atomic operations
        async with db.transaction() as tx:
            await tx.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
            await tx.execute("INSERT INTO users (name) VALUES (?)", ("Charlie",))
            # Both inserts will be committed together, or both rolled back if an error occurs
    """

    def __init__(self, db_path: str):
        """Initialize SQLite database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self._db_path = db_path
        self._conn: Optional[aiosqlite.Connection] = None
        self._is_in_memory = db_path == ":memory:"

    async def _get_connection(self) -> aiosqlite.Connection:
        """Get database connection, reusing for in-memory databases."""
        if self._is_in_memory:
            if self._conn is None:
                self._conn = await aiosqlite.connect(self._db_path)
            return self._conn
        else:
            return aiosqlite.connect(self._db_path)

    async def execute(self, query: str, params: tuple) -> None:
        """Execute a SQL query that modifies the database.

        Args:
            query: SQL query string with ? placeholders
            params: Tuple of parameter values to insert into query

        Example:
            await db.execute(
                "INSERT INTO users (name, age) VALUES (?, ?)",
                ("Bob", 25)
            )
        """
        if self._is_in_memory:
            conn = await self._get_connection()
            await conn.execute(query, params)
            await conn.commit()
        else:
            async with aiosqlite.connect(self._db_path) as conn:
                await conn.execute(query, params)
                await conn.commit()

    async def query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SQL query that retrieves data.

        Args:
            query: SQL query string with ? placeholders
            params: Tuple of parameter values to insert into query

        Returns:
            List of dictionaries representing database rows

        Example:
            rows = await db.query(
                "SELECT name FROM users WHERE age > ?",
                (21,)
            )
            # Returns: [{"name": "Alice"}, {"name": "Bob"}]
        """
        if self._is_in_memory:
            conn = await self._get_connection()
            conn.row_factory = aiosqlite.Row
            cursor = await conn.execute(query, params)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
        else:
            async with aiosqlite.connect(self._db_path) as conn:
                conn.row_factory = aiosqlite.Row
                cursor = await conn.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator["Tx", None]:
        """Context manager for database transactions.

        Ensures all operations within the transaction are atomic.
        If an exception occurs, the transaction is rolled back.
        If no exception occurs, the transaction is committed.

        Example:
            async with db.transaction() as tx:
                await tx.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
                await tx.execute("INSERT INTO users (name) VALUES (?)", ("Bob",))
        """
        if self._is_in_memory:
            # For in-memory databases, use the existing connection
            conn = await self._get_connection()
            try:
                yield Tx(conn)
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise e
        else:
            # For file databases, create a new connection for the transaction
            async with aiosqlite.connect(self._db_path) as conn:
                try:
                    yield Tx(conn)
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None


class Tx(ISqlDb):
    """A transaction wrapper that implements the same interface as SqlDb.

    This allows code to be agnostic to whether it's working with a regular
    database connection or a transaction.
    """

    def __init__(self, conn: aiosqlite.Connection):
        """Initialize transaction with a database connection.

        Args:
            conn: The database connection to use for this transaction
        """
        self._conn = conn

    async def execute(self, query: str, params: tuple = ()) -> None:
        """Execute a SQL query within the transaction.

        Args:
            query: SQL query string with ? placeholders
            params: Tuple of parameter values to insert into query
        """
        await self._conn.execute(query, params)

    async def query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """Execute a SQL query within the transaction that retrieves data.

        Args:
            query: SQL query string with ? placeholders
            params: Tuple of parameter values to insert into query

        Returns:
            List of dictionaries representing database rows
        """
        self._conn.row_factory = aiosqlite.Row
        cursor = await self._conn.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]
