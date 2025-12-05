def cast(cast_value, cast_type, cast_default):
    try:
        return cast_value if isinstance(cast_value, cast_type) else cast_type(cast_value)
    except (TypeError, ValueError):
        return cast_default

def equals(a: float, b: float, rel: float = 1e-12, abs_: float = 1e-12) -> bool:
    return abs(a - b) <= max(rel * max(1.0, abs(a), abs(b)), abs_)

def contains(text: str, substrings: str | tuple | list, case_sensitive: bool = False) -> bool:
    if isinstance(substrings, str): substrings = [substrings]
    if isinstance(substrings, tuple): substrings = list(substrings)
    if not case_sensitive:
        text = text.lower()
        substrings = [s.lower() for s in substrings]
    return any(sub in text for sub in substrings)
