from src.library.sql_db import Tx
from src.library.sql import Sql
from typing import Dict, Any


class UserSessionDb:
    async def up(self, tx: Tx):
        up = [
            """
            CREATE TABLE IF NOT EXISTS user_sessions (
                user_session__id TEXT PRIMARY KEY,
                user_session__user_id TEXT,
                user_session__login_link_id TEXT,
                user_session__session_id TEXT,
                user_session__created_at_utc_iso TEXT,
                user_session__expires_at_utc_iso TEXT
            )
            """,
            """
            CREATE INDEX IF NOT EXISTS user_sessions_user_session__user_id_index ON user_sessions (user_session__user_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS user_sessions_user_session__login_link_id_index ON user_sessions (user_session__login_link_id)
            """,
            """
            CREATE INDEX IF NOT EXISTS user_sessions_user_session__session_id_index ON user_sessions (user_session__session_id)
            """,
        ]
        for sql in up:
            await tx.execute(sql)

    async def insert(self, tx: Tx, user_session: Dict[str, Any]) -> None:
        sql, params = Sql.dict_to_insert("user_sessions", user_session)
        await tx.execute(sql, params)

    async def find_by_session_id(
        self, tx: Tx, user_session__session_id: str
    ) -> Dict[str, Any]:
        found = await tx.query(
            "SELECT * FROM user_sessions WHERE user_session__session_id = ? LIMIT 1",
            (user_session__session_id,),
        )
        return found[0]
