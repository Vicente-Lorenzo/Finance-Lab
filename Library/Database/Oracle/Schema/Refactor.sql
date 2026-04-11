BEGIN
    RAISE_APPLICATION_ERROR(-20000, 'Schema refactor is not supported via SQL in Oracle. Schemas are owned by users.');
END;
