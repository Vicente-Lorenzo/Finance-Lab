import pytest

from Library.Database.Query import QueryAPI

PG_TOKEN = lambda i: "%s"
MSSQL_TOKEN = lambda i: "%s"
ORACLE_TOKEN = lambda i: f":{i}"

def test_interpolation():
    q = QueryAPI("SELECT * FROM ::schema::.::table::")
    query, parameters = q(PG_TOKEN, schema="public", table="users")
    assert query == "SELECT * FROM public.users"
    assert parameters is None

def test_positional():
    q = QueryAPI("SELECT * FROM t WHERE a = :?: AND b = :?:")
    query, parameters = q(PG_TOKEN, 10, 20)
    assert query == "SELECT * FROM t WHERE a = %s AND b = %s"
    assert parameters == (10, 20)

def test_named_compiles_to_positional():
    q = QueryAPI("SELECT * FROM t WHERE id = :id: AND s = :status:")
    query, parameters = q(PG_TOKEN, id=7, status="ACTIVE")
    assert query == "SELECT * FROM t WHERE id = %s AND s = %s"
    assert parameters == (7, "ACTIVE")

def test_named_and_positional_ordering():
    q = QueryAPI("SELECT * FROM t WHERE id = :id: AND s = :?: AND x = :x:")
    query, parameters = q(PG_TOKEN, "SVAL", id=1, x=3)
    assert query == "SELECT * FROM t WHERE id = %s AND s = %s AND x = %s"
    assert parameters == (1, "SVAL", 3)

def test_duplicate_named_parameter():
    q = QueryAPI("SELECT * FROM t WHERE a = :id: OR b = :id:")
    query, parameters = q(PG_TOKEN, id=99)
    assert query == "SELECT * FROM t WHERE a = %s OR b = %s"
    assert parameters == (99, 99)

def test_interpolation_and_named():
    q = QueryAPI("SELECT * FROM ::schema::.::table:: WHERE id = :id:")
    query, parameters = q(PG_TOKEN, schema="public", table="users", id=5)
    assert query == "SELECT * FROM public.users WHERE id = %s"
    assert parameters == (5,)

def test_missing_positional():
    q = QueryAPI("SELECT * FROM t WHERE a = :?: AND b = :?:")
    with pytest.raises(ValueError):
        q(PG_TOKEN, 10)

def test_missing_named():
    q = QueryAPI("SELECT * FROM t WHERE id = :id:")
    with pytest.raises(KeyError):
        q(PG_TOKEN)  # id missing

def test_numbered_placeholders():
    q = QueryAPI("SELECT * FROM t WHERE a = :?: AND b = :x: AND c = :?:")
    query, parameters = q(ORACLE_TOKEN, "A", "C", x="B")
    assert query == "SELECT * FROM t WHERE a = :1 AND b = :2 AND c = :3"
    assert parameters == ("A", "B", "C")
