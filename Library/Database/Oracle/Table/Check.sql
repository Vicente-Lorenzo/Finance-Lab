SELECT 1
FROM all_tables
WHERE owner = UPPER('::schema::') AND table_name = UPPER('::table::');
