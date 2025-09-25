class Sql:
    @staticmethod
    def dict_to_insert(table: str, dict: dict):
        columns = ", ".join([f"{key}" for key in sorted(dict.keys())])
        values = ", ".join([f"?" for _ in sorted(dict.keys())])
        params = tuple(dict[key] for key in sorted(dict.keys()))
        return f"INSERT INTO {table} ({columns}) VALUES ({values})", params
