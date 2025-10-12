def cast(cast_value, cast_type, cast_default):
    try:
        return cast_value if isinstance(cast_value, cast_type) else cast_type(cast_value)
    except (TypeError, ValueError):
        return cast_default
