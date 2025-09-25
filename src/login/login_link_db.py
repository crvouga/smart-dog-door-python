import json
from src.library.sql_db import SqlDb


class LoginLinkDb:
    def __init__(self, sql_db: SqlDb):
        self._sql_db = sql_db

    def add(self, login_link: dict):
        self._sql_db.execute(
            "INSERT INTO entities (id, type, data) VALUES (?, ?, ?)",
            (login_link["login_link.id"], "login_link", json.dumps(login_link)),
        )

    def find_by_token(self, login_link_token: str) -> dict | None:
        queried = self._sql_db.query(
            "SELECT data FROM entities WHERE type = 'login_link' AND data LIKE '%login_link.token% = ?'",
            (login_link_token,),
        )

        if len(queried) == 0:
            return None

        return json.loads(queried[0]["data"])
