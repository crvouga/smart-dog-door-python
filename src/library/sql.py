class Sql:
    @staticmethod
    def dict_to_insert(table: str, dict: dict):
        columns = ", ".join([f"{key}" for key in sorted(dict.keys())])
        values = ", ".join([f"?" for _ in sorted(dict.keys())])
        params = tuple(dict[key] for key in sorted(dict.keys()))
        return f"INSERT INTO {table} ({columns}) VALUES ({values})", params

    @staticmethod
    def dict_to_update_one_by_primary_key(table: str, dict: dict, primary_key: str):
        update_cols = [k for k in sorted(dict.keys()) if k != primary_key]
        set_clause = ", ".join([f"{col} = ?" for col in update_cols])
        params = tuple(dict[col] for col in update_cols)
        params = params + (dict[primary_key],)  # Add primary key value as last param
        return f"UPDATE {table} SET {set_clause} WHERE {primary_key} = ?", params
