BEGIN
    RAISE_APPLICATION_ERROR(-20000, 'Database refactor is not supported via SQL in Oracle. Use the DBNEWID (NID) utility.');
END;
