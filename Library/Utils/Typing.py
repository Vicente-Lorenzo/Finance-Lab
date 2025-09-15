def cast(cast_value, cast_type, cast_default):
    try:
        return cast_type(cast_value)
    except (TypeError, ValueError):
        return cast_default
