WITH expected_structure(column_name, data_type) AS (VALUES {definitions}),
actual_structure AS (SELECT column_name, data_type FROM information_schema.columns WHERE table_schema = '{schema}' AND table_name = '{table}')
SELECT e.column_name, e.data_type, a.column_name, a.data_type
FROM expected_structure e
FULL OUTER JOIN actual_structure a
    ON e.column_name = a.column_name
    AND e.data_type = a.data_type
WHERE a.column_name IS NULL OR e.column_name IS NULL;
