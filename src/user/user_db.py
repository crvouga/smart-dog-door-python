from src.library.sql_db import SqlDb
from src.library.sql import Sql
from typing import Dict, Any


class UserDb:
    def __init__(self, sql_db: SqlDb):
        self._sql_db = sql_db

    def up(self) -> list[str]:
        return [
            """
            CREATE TABLE IF NOT EXISTS users (
                user__id TEXT PRIMARY KEY,
                user__email_address TEXT,
                user__password TEXT
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS users_user__email_address_index ON users (user__email_address)
            """,
        ]

    async def insert(self, user: Dict[str, Any]) -> None:
        sql, params = Sql.dict_to_insert("users", user)
        await self._sql_db.execute(sql, params)

    async def find_by_email_address(self, user__email_address: str) -> Dict[str, Any]:
        found = await self._sql_db.query(
            "SELECT * FROM users WHERE user__email_address = ? LIMIT 1",
            (user__email_address,),
        )
        return found[0]
