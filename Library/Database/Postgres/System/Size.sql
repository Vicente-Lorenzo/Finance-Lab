SELECT 
    current_database()::text AS "Database",
    n.nspname AS "Schema",
    c.relname AS "Table",
    pg_total_relation_size(c.oid) AS "Size",
    pg_size_pretty(pg_total_relation_size(c.oid)) AS "Formatted"
FROM pg_class c
JOIN pg_namespace n ON n.oid = c.relnamespace
WHERE n.nspname LIKE :schema:
  AND c.relname LIKE :table:
  AND c.relkind = 'r'
  AND n.nspname NOT IN ('pg_catalog', 'information_schema')
ORDER BY "Size" DESC;