from datetime import datetime, date, time

def datetime_to_string(dt: datetime | date | time, fmt: str) -> str:
    return dt.strftime(fmt)

def string_to_datetime(date_str: str, fmt_str: str) -> datetime:
    return datetime.strptime(date_str, fmt_str)

def datetime_to_timestamp(dt: datetime | date | time, milliseconds: bool = False) -> float:
    ts = dt.timestamp()
    return ts * 1000 if milliseconds else ts

def timestamp_to_datetime(ts: float, milliseconds: bool = False) -> datetime:
    return datetime.fromtimestamp(ts / 1000 if milliseconds else ts)

def datetime_to_iso(dt: datetime) -> str:
    return dt.isoformat()

def iso_to_datetime(iso_str: str) -> datetime:
    return datetime.fromisoformat(iso_str)

