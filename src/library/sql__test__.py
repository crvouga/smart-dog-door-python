from src.library.sql import Sql
from typing import Any


def test_dict_to_insert_generates_correct_sql_and_params() -> None:
    # Arrange
    table = "test_table"
    dict_to_insert: dict[str, Any] = {
        "column_a": "value_a",
        "column_b": "value_b",
        "column_c": "value_c",
    }

    # Act
    sql, params = Sql.dict_to_insert(table, dict_to_insert)

    # Assert
    expected_sql = (
        "INSERT INTO test_table (column_a, column_b, column_c) VALUES (?, ?, ?)"
    )
    expected_params = ("value_a", "value_b", "value_c")

    assert sql == expected_sql
    assert params == expected_params


def test_dict_to_insert_handles_empty_dict() -> None:
    # Arrange
    table = "test_table"
    dict_to_insert: dict[str, Any] = {}

    # Act
    sql, params = Sql.dict_to_insert(table, dict_to_insert)

    # Assert
    expected_sql = "INSERT INTO test_table () VALUES ()"
    expected_params = ()

    assert sql == expected_sql
    assert params == expected_params


def test_dict_to_insert_preserves_value_types() -> None:
    # Arrange
    table = "test_table"
    dict_to_insert: dict[str, Any] = {
        "string_col": "string_value",
        "int_col": 42,
        "float_col": 3.14,
        "none_col": None,
    }

    # Act
    sql, params = Sql.dict_to_insert(table, dict_to_insert)

    # Assert
    # Keys are sorted alphabetically: float_col, int_col, none_col, string_col
    assert isinstance(params[0], float)  # float_col
    assert isinstance(params[1], int)  # int_col
    assert params[2] is None  # none_col
    assert isinstance(params[3], str)  # string_col
