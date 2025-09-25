import aiosqlite
from contextlib import asynccontextmanager


class SqlDb:
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
        async with db.transaction() as conn:
            await db.execute_in_transaction(conn, "INSERT INTO users (name) VALUES (?)", ("Bob",))
            await db.execute_in_transaction(conn, "INSERT INTO users (name) VALUES (?)", ("Charlie",))
            # Both inserts will be committed together, or both rolled back if an error occurs
    """

    def __init__(self, db_path: str):
        """Initialize SQLite database connection.

        Args:
            db_path: Path to the SQLite database file
        """
        self._db_path = db_path
        self._conn = None
        self._is_in_memory = db_path == ":memory:"

    async def _get_connection(self):
        """Get database connection, reusing for in-memory databases."""
        if self._is_in_memory:
            if self._conn is None:
                self._conn = await aiosqlite.connect(self._db_path)
            return self._conn
        else:
            return aiosqlite.connect(self._db_path)

    async def execute(self, query: str, params: tuple):
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

    async def query(self, query: str, params: tuple = ()):
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
    async def transaction(self):
        """Context manager for database transactions.

        Ensures all operations within the transaction are atomic.
        If an exception occurs, the transaction is rolled back.
        If no exception occurs, the transaction is committed.

        Example:
            async with db.transaction() as conn:
                await db.execute_in_transaction(conn, "INSERT INTO users (name) VALUES (?)", ("Alice",))
                await db.execute_in_transaction(conn, "INSERT INTO users (name) VALUES (?)", ("Bob",))
        """
        if self._is_in_memory:
            # For in-memory databases, use the existing connection
            conn = await self._get_connection()
            try:
                yield conn
                await conn.commit()
            except Exception as e:
                await conn.rollback()
                raise e
        else:
            # For file databases, create a new connection for the transaction
            async with aiosqlite.connect(self._db_path) as conn:
                try:
                    yield conn
                    await conn.commit()
                except Exception as e:
                    await conn.rollback()
                    raise e

    async def execute_in_transaction(self, conn, query: str, params: tuple):
        """Execute a SQL query within a transaction.

        Args:
            conn: Database connection from transaction context
            query: SQL query string with ? placeholders
            params: Tuple of parameter values to insert into query
        """
        await conn.execute(query, params)

    async def query_in_transaction(self, conn, query: str, params: tuple):
        """Execute a SQL query within a transaction that retrieves data.

        Args:
            conn: Database connection from transaction context
            query: SQL query string with ? placeholders
            params: Tuple of parameter values to insert into query

        Returns:
            List of dictionaries representing database rows
        """
        conn.row_factory = aiosqlite.Row
        cursor = await conn.execute(query, params)
        rows = await cursor.fetchall()
        return [dict(row) for row in rows]

    async def close(self):
        """Close the database connection."""
        if self._conn is not None:
            await self._conn.close()
            self._conn = None
