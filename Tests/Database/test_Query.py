import pytest

from Library.Database.Query import QueryAPI

PG_TOKEN = lambda i: "%s"
MSSQL_TOKEN = lambda i: "%s"
ORACLE_TOKEN = lambda i: f":{i}"

def test_interpolation_only():
    q = QueryAPI("SELECT * FROM ::schema::.::table::")
    sql, params = q(PG_TOKEN, schema="public", table="users")
    assert sql == "SELECT * FROM public.users"
    assert params is None

def test_positional_only():
    q = QueryAPI("SELECT * FROM t WHERE a = :?: AND b = :?:")
    sql, params = q(PG_TOKEN, 10, 20)
    assert sql == "SELECT * FROM t WHERE a = %s AND b = %s"
    assert params == (10, 20)


def test_named_only_compiles_to_positional():
    q = QueryAPI("SELECT * FROM t WHERE id = :id: AND s = :status:")
    sql, params = q(PG_TOKEN, id=7, status="ACTIVE")
    assert sql == "SELECT * FROM t WHERE id = %s AND s = %s"
    assert params == (7, "ACTIVE")


def test_mixed_named_and_positional_ordering():
    q = QueryAPI("SELECT * FROM t WHERE id = :id: AND s = :?: AND x = :x:")
    sql, params = q(PG_TOKEN, "SVAL", id=1, x=3)
    assert sql == "SELECT * FROM t WHERE id = %s AND s = %s AND x = %s"
    assert params == (1, "SVAL", 3)


def test_duplicate_named_parameter_appends_twice():
    q = QueryAPI("SELECT * FROM t WHERE a = :id: OR b = :id:")
    sql, params = q(PG_TOKEN, id=99)
    assert sql == "SELECT * FROM t WHERE a = %s OR b = %s"
    assert params == (99, 99)


def test_interpolation_keys_removed_not_used_as_named_param():
    # schema/table are interpolations; :id: is a named value param.
    q = QueryAPI("SELECT * FROM ::schema::.::table:: WHERE id = :id:")
    sql, params = q(PG_TOKEN, schema="public", table="users", id=5)
    assert sql == "SELECT * FROM public.users WHERE id = %s"
    assert params == (5,)


def test_missing_positional_args_raises():
    q = QueryAPI("SELECT * FROM t WHERE a = :?: AND b = :?:")
    with pytest.raises(ValueError):
        q(PG_TOKEN, 10)  # missing second arg


def test_missing_named_param_raises():
    q = QueryAPI("SELECT * FROM t WHERE id = :id:")
    with pytest.raises(KeyError):
        q(PG_TOKEN)  # id missing


def test_oracle_numbered_placeholders():
    q = QueryAPI("SELECT * FROM t WHERE a = :?: AND b = :x: AND c = :?:")
    sql, params = q(ORACLE_TOKEN, "A", "C", x="B")
    assert sql == "SELECT * FROM t WHERE a = :1 AND b = :2 AND c = :3"
    assert params == ("A", "B", "C")


def test_postgres_token_is_constant():
    q = QueryAPI("SELECT * FROM t WHERE a = :?: AND b = :?: AND c = :?:")
    sql, params = q(PG_TOKEN, 1, 2, 3)
    assert sql.count("%s") == 3
    assert params == (1, 2, 3)
