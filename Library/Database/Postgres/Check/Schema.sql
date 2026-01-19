SELECT schema_name
FROM information_schema.schemata
WHERE catalog_name = '{database}' AND schema_name = '{schema}';
