def equals(a: float, b: float, rel: float = 1e-12, abs_: float = 1e-12) -> bool:
    return abs(a - b) <= max(rel * max(1.0, abs(a), abs(b)), abs_)
