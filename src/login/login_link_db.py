from src.library.sql_db import Tx
from src.library.sql import Sql
from typing import Dict, Any


class LoginLinkDb:
    async def up(self, tx: Tx):
        up = [
            """
            CREATE TABLE IF NOT EXISTS login_links (
                login_link__id TEXT PRIMARY KEY,
                login_link__email_address TEXT,
                login_link__token TEXT,
                login_link__requested_at_utc_iso TEXT,
                login_link__status TEXT,
                login_link__email_id TEXT,
                login_link__used_at_utc_iso TEXT
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS login_links_login_link__token_index ON login_links (login_link__token)
            """,
        ]
        for sql in up:
            await tx.execute(sql)

    async def insert(self, tx: Tx, login_link: Dict[str, Any]) -> None:
        sql, params = Sql.dict_to_insert("login_links", login_link)
        await tx.execute(sql, params)

    async def update(self, tx: Tx, login_link: Dict[str, Any]) -> None:
        sql, params = Sql.dict_to_update_one_by_primary_key(
            "login_links", login_link, "login_link__id"
        )
        await tx.execute(sql, params)

    async def find_by_token(self, tx: Tx, login_link__token: str) -> Dict[str, Any]:
        found = await tx.query(
            f"SELECT * FROM login_links WHERE login_link__token = ? LIMIT 1",
            (login_link__token,),
        )
        if not found:
            raise IndexError("Token not found")

        row = found[0]
        return row
