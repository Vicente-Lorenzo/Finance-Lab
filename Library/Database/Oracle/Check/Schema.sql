SELECT 1
FROM all_users
WHERE username = UPPER('::schema::');
