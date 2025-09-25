from src.library.sql_db import SqlDb
from src.library.sql import Sql
from typing import Dict, Any


class LoginLinkDb:
    def __init__(self, sql_db: SqlDb):
        self._sql_db = sql_db

    def up(self) -> list[str]:
        return [
            """
            CREATE TABLE IF NOT EXISTS login_links (
                login_link__id TEXT PRIMARY KEY,
                login_link__email_address TEXT,
                login_link__token TEXT,
                login_link__requested_at_utc_iso TEXT,
                login_link__status TEXT
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS login_links_login_link__token_index ON login_links (login_link__token)
            """,
            """
            ALTER TABLE login_links ADD COLUMN login_link__email_id TEXT
            """,
        ]

    async def insert(self, login_link: Dict[str, Any]) -> None:
        sql, params = Sql.dict_to_insert("login_links", login_link)
        await self._sql_db.execute(sql, params)

    async def find_by_token(self, login_link__token: str) -> Dict[str, Any]:
        found = await self._sql_db.query(
            f"SELECT * FROM login_links WHERE login_link__token = ? LIMIT 1",
            (login_link__token,),
        )
        if not found:
            raise IndexError("Token not found")

        row = found[0]
        return row
