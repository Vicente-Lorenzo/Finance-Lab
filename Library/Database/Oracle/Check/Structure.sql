WITH expected_structure AS (
    ::definitions::
),
actual_structure AS (
    SELECT column_name, data_type
    FROM all_tab_columns
    WHERE owner      = UPPER('::schema::')
      AND table_name = UPPER('::table::')
)
SELECT
    e.column_name AS expected_column_name,
    e.data_type   AS expected_data_type,
    a.column_name AS actual_column_name,
    a.data_type   AS actual_data_type
FROM expected_structure e
FULL OUTER JOIN actual_structure a
  ON UPPER(e.column_name) = UPPER(a.column_name)
 AND UPPER(e.data_type)   = UPPER(a.data_type)
WHERE a.column_name IS NULL OR e.column_name IS NULL;
