class SqlDb:
    def __init__(self, db_path: str):
        self._db_path = db_path

    def execute(self, query: str, params: tuple):
        pass

    def query(self, query: str, params: tuple):
        pass
