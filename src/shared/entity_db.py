from src.library.sql_db import SqlDb
import json


class EntityDb:
    def __init__(self, sql_db: SqlDb):
        self._sql_db = sql_db

    def insert(self, type, id: str, entity: dict):

        entity["type"] = type

        self._sql_db.execute(
            "INSERT INTO entities (id, type, data) VALUES (?, ?, ?)",
            (entity["id"], entity["type"], json.dumps(entity)),
        )
