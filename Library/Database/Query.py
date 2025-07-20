import hashlib
from pathlib import Path

from Library.Database import DatabaseAPI
from Library.Parameters import ParametersAPI

def main():
    # --------------------------------------------------------------------------
    # LOAD SETTINGS
    # --------------------------------------------------------------------------
    parameters = ParametersAPI().Watchlist

    BROKERS = parameters.Brokers
    SYMBOLS = [symbol for group in parameters.Symbols.values() for symbol in group]
    TIMEFRAMES = parameters.Timeframes
    
    # --------------------------------------------------------------------------
    # HELPER FUNCTIONS: no DO blocks, no separate _sql names.
    # Using psql \gexec for conditional logic
    # --------------------------------------------------------------------------
    def generate_password(input_string: str):
        return hashlib.sha256(input_string.encode()).hexdigest()

    def create_role_if_not_exists(role_name: str, password: str):
        """
        1) Create only if it doesn't exist (using psql \gexec).
        2) Then alter to ensure the password is updated.
        """
        return f"""
SELECT 'CREATE ROLE "{role_name}" LOGIN'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_roles WHERE rolname = '{role_name}'
)
\\gexec

ALTER ROLE "{role_name}" WITH LOGIN PASSWORD '{password}';
"""

    def create_db_if_not_exists(db_name: str, owner_name: str):
        """
        Conditionally create a database using psql \gexec (no DO block).
        """
        return f"""
SELECT 'CREATE DATABASE "{db_name}" OWNER "{owner_name}"'
WHERE NOT EXISTS (
    SELECT 1 FROM pg_database WHERE datname = '{db_name}'
)
\\gexec

"""

    def create_schema_if_not_exists(schema_name: str, schema_owner: str):
        return f'CREATE SCHEMA IF NOT EXISTS "{schema_name}" AUTHORIZATION "{schema_owner}";\n'

    def create_table_if_not_exists(schema_name: str, table_name: str):
        return f'CREATE TABLE IF NOT EXISTS "{schema_name}"."{table_name}" ();\n'

    def add_column_if_not_exists(schema_name: str, table_name: str, column_name: str, data_type: str):
        return (
            f'ALTER TABLE "{schema_name}"."{table_name}" '
            f'ADD COLUMN IF NOT EXISTS "{column_name}" {data_type};\n'
        )

    def grant_usage_on_schema(schema_name: str, role_name: str):
        return f'GRANT USAGE ON SCHEMA "{schema_name}" TO "{role_name}";\n'

    def grant_privileges_on_table(schema_name: str, table_name: str, role_name: str, privileges: list):
        privs_joined = ", ".join(privileges)
        return f'GRANT {privs_joined} ON "{schema_name}"."{table_name}" TO "{role_name}";\n'

    def add_primary_key_if_not_exists(schema_name: str, table_name: str, key_name: str, column_name: str):
        """
        Similar approach with \gexec to ensure the constraint only gets added if missing.
        """
        return f"""
SELECT 'ALTER TABLE "{schema_name}"."{table_name}" ADD CONSTRAINT {key_name} PRIMARY KEY ("{column_name}")'
WHERE NOT EXISTS (
    SELECT 1
    FROM pg_constraint
    WHERE conrelid = '"{schema_name}"."{table_name}"'::regclass
      AND conname = '{key_name}'
)
\\gexec

"""

    # --------------------------------------------------------------------------
    # 1) BUILD THE CREATE/UPDATE SCRIPT
    # --------------------------------------------------------------------------
    create_script = []

    for broker in BROKERS:
        broker_owner = f"{broker}_Owner"
        broker_owner_pass = generate_password(broker_owner)

        # Create/alter broker role
        create_script.append(create_role_if_not_exists(broker_owner, broker_owner_pass))

        # Create DB if not exists
        create_script.append(create_db_if_not_exists(broker, broker_owner))

        # Connect to that DB
        create_script.append(f'\\connect "{broker}"\n')

        for symbol in SYMBOLS:
            asset_owner = f"{broker}_{symbol}_Owner"
            asset_owner_pass = generate_password(asset_owner)

            create_script.append(create_role_if_not_exists(asset_owner, asset_owner_pass))
            create_script.append(create_schema_if_not_exists(symbol, asset_owner))

            # Symbol table
            create_script.append(create_table_if_not_exists(symbol, "Symbol"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_BASEASSET,      "VARCHAR"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_QUOTEASSET,      "VARCHAR"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_DIGITS,            "INT"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_PIPSIZE,           "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_POINTSIZE, "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_LOTSIZE,           "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_VOLUMEINUNITSMIN,  "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_VOLUMEINUNITSMAX,  "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_VOLUMEINUNITSSTEP, "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_COMMISSION,        "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_COMMISSIONMODE, "VARCHAR"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_SWAPLONG,          "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_SWAPSHORT,         "DOUBLE PRECISION"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_SWAPMODE, "VARCHAR"))
            create_script.append(add_column_if_not_exists(symbol, "Symbol", DatabaseAPI.SYMBOL_SWAP3DAYROLLOVER,  "VARCHAR"))

            # Insert default row if table is empty
            create_script.append(
                f'INSERT INTO "{symbol}"."Symbol" '
                f"SELECT 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '0', 0, 0, '0', '0' "
                f'WHERE NOT EXISTS (SELECT 1 FROM "{symbol}"."Symbol");\n'
            )

            # Timeframes
            for timeframe in TIMEFRAMES:
                timeframe_owner = f"{broker}_{symbol}_{timeframe}_Owner"
                timeframe_owner_pass = generate_password(timeframe_owner)
                timeframe_user = f"{broker}_{symbol}_{timeframe}_User"
                timeframe_user_pass = generate_password(timeframe_user)

                create_script.append(create_role_if_not_exists(timeframe_owner, timeframe_owner_pass))
                create_script.append(create_role_if_not_exists(timeframe_user, timeframe_user_pass))

                create_script.append(create_table_if_not_exists(symbol, timeframe))
                create_script.append(add_column_if_not_exists(symbol, timeframe, DatabaseAPI.MARKET_TIMESTAMP,  "TIMESTAMP"))
                create_script.append(add_column_if_not_exists(symbol, timeframe, DatabaseAPI.MARKET_OPENPRICE,  "DOUBLE PRECISION"))
                create_script.append(add_column_if_not_exists(symbol, timeframe, DatabaseAPI.MARKET_HIGHPRICE,  "DOUBLE PRECISION"))
                create_script.append(add_column_if_not_exists(symbol, timeframe, DatabaseAPI.MARKET_LOWPRICE,   "DOUBLE PRECISION"))
                create_script.append(add_column_if_not_exists(symbol, timeframe, DatabaseAPI.MARKET_CLOSEPRICE, "DOUBLE PRECISION"))
                create_script.append(add_column_if_not_exists(symbol, timeframe, DatabaseAPI.MARKET_TICKVOLUME, "INT"))

                # Primary key if not exists
                pk_name = f"{timeframe}_pkey"
                create_script.append(
                    add_primary_key_if_not_exists(symbol, timeframe, pk_name, DatabaseAPI.MARKET_TIMESTAMP)
                )

                # Change table owner
                create_script.append(f'ALTER TABLE "{symbol}"."{timeframe}" OWNER TO "{timeframe_owner}";\n')

                # Grants
                create_script.append(grant_usage_on_schema(symbol, timeframe_user))
                create_script.append(grant_privileges_on_table(symbol, "Symbol", timeframe_user, ["SELECT","INSERT","UPDATE"]))
                create_script.append(grant_privileges_on_table(symbol, timeframe, timeframe_user, ["SELECT","INSERT","UPDATE"]))

    # Write the CREATE/UPDATE script
    create_path = Path.cwd() / "QueryCreateOrUpdate.sql"
    with create_path.open("w", encoding="utf-8") as f:
        f.write("".join(create_script))

    print(f"Create/Update script generated at: {create_path}")

    # --------------------------------------------------------------------------
    # 2) BUILD THE DELETE SCRIPT
    # --------------------------------------------------------------------------
    delete_script = []

    for broker in BROKERS:
        broker_owner = f"{broker}_Owner"

        # 1) Connect to each broker DB (if it exists) to drop tables & schemas
        delete_script.append(f'\\connect \"{broker}\"\n')

        for symbol in SYMBOLS:
            # Drop timeframe tables
            for timeframe in TIMEFRAMES:
                delete_script.append(f'DROP TABLE IF EXISTS \"{symbol}\".\"{timeframe}\" CASCADE;\n')
            # Drop Symbol table and schema
            delete_script.append(f'DROP TABLE IF EXISTS \"{symbol}\".\"Symbol\" CASCADE;\n')
            delete_script.append(f'DROP SCHEMA IF EXISTS \"{symbol}\" CASCADE;\n')

        # 2) Connect back to 'postgres' to drop the DB
        delete_script.append('\\connect postgres\n')

        # 3) Reassign the DB owner to 'postgres' (prevents role dependency errors)
        delete_script.append(f'ALTER DATABASE \"{broker}\" OWNER TO postgres;\n')

        # 4) Drop the DB (with FORCE for Postgres 15+; remove it if on older Postgres)
        delete_script.append(f'DROP DATABASE IF EXISTS \"{broker}\" WITH (FORCE);\n')

        # 5) Drop roles
        for symbol in SYMBOLS:
            asset_owner = f"{broker}_{symbol}_Owner"
            for timeframe in TIMEFRAMES:
                timeframe_owner = f"{broker}_{symbol}_{timeframe}_Owner"
                timeframe_user = f"{broker}_{symbol}_{timeframe}_User"

                delete_script.append(f'DROP ROLE IF EXISTS \"{timeframe_user}\";\n')
                delete_script.append(f'DROP ROLE IF EXISTS \"{timeframe_owner}\";\n')
            delete_script.append(f'DROP ROLE IF EXISTS \"{asset_owner}\";\n')

        # 6) Finally drop the broker role
        delete_script.append(f'DROP ROLE IF EXISTS \"{broker_owner}\";\n\n')

    # Write the DELETE script
    delete_path = Path.cwd() / "QueryDelete.sql"
    with delete_path.open("w", encoding="utf-8") as f:
        f.write("".join(delete_script))

    print(f"Delete script generated at: {delete_path}")


if __name__ == "__main__":
    main()
