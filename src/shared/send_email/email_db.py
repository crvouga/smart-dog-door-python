from src.library.sql_db import SqlDb
from src.library.sql import Sql
from typing import Dict, Any


class EmailDb:
    def __init__(self, sql_db: SqlDb):
        self._sql_db = sql_db

    def up(self) -> list[str]:
        return [
            """
            CREATE TABLE IF NOT EXISTS emails (
                email__id TEXT PRIMARY KEY,
                email__to TEXT,
                email__subject TEXT,
                email__body TEXT,
                email__sent_at_utc_iso TEXT
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS emails_email__to_index ON emails (email__to)
            """,
        ]

    async def insert(self, email: Dict[str, Any]) -> None:
        sql, params = Sql.dict_to_insert("emails", email)
        await self._sql_db.execute(sql, params)

    async def find_by_id(self, email__id: str) -> Dict[str, Any]:
        found = await self._sql_db.query(
            f"SELECT * FROM emails WHERE email__id = ? LIMIT 1",
            (email__id,),
        )
        return found[0]
