SELECT
    table_catalog AS [Database],
    table_schema AS [Schema],
    table_name AS [Table],
    column_name AS [Column]
FROM information_schema.columns
WHERE table_catalog LIKE :database:
  AND table_schema LIKE :schema:
  AND table_name LIKE :table:
  AND column_name LIKE :column:
  AND table_schema NOT IN ('sys', 'INFORMATION_SCHEMA', 'guest')
ORDER BY table_catalog, table_schema, table_name, ordinal_position;
