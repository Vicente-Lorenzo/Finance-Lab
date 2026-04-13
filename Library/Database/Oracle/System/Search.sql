SELECT
    SYS_CONTEXT('USERENV', 'CON_NAME') AS "Database",
    c.owner AS "Schema",
    c.table_name AS "Table",
    c.column_name AS "Column"
FROM all_tab_columns c
WHERE SYS_CONTEXT('USERENV', 'CON_NAME') LIKE :database:
  AND c.owner LIKE UPPER(CASE WHEN :schema: = '%%' THEN '%%' ELSE :schema: END)
  AND c.table_name LIKE UPPER(CASE WHEN :table: = '%%' THEN '%%' ELSE :table: END)
  AND c.column_name LIKE UPPER(CASE WHEN :column: = '%%' THEN '%%' ELSE :column: END)
  AND c.owner NOT IN ('SYS', 'SYSTEM', 'OUTLN', 'CTXSYS', 'XDB', 'AUDSYS', 'APPQOSSYS', 'DBSNMP', 'ORACLE_OCM', 'DBSFWUSER', 'OJVMSYS', 'WMSYS', 'ANONYMOUS')
ORDER BY c.owner, c.table_name, c.column_id;
