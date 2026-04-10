DECLARE @sql NVARCHAR(MAX) = N'KILL ' + CAST(:id: AS NVARCHAR(10)) + N';';
EXEC sp_executesql @sql;