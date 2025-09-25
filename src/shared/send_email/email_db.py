from src.library.sql_db import Tx
from src.library.sql import Sql
from typing import Dict, Any


class EmailDb:
    async def up(self, tx: Tx):
        up = [
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
        for sql in up:
            await tx.execute(sql)

    async def insert(self, tx: Tx, email: Dict[str, Any]) -> None:
        sql, params = Sql.dict_to_insert("emails", email)
        await tx.execute(sql, params)

    async def find_by_id(self, tx: Tx, email__id: str) -> Dict[str, Any]:
        found = await tx.query(
            f"SELECT * FROM emails WHERE email__id = ? LIMIT 1",
            (email__id,),
        )
        return found[0]
