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

def seconds_to_string(seconds: float) -> str:
    seconds, milliseconds = divmod(seconds, 1)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    months, days = divmod(days, 12)
    years, months = divmod(months, 12)
    result = []
    if years:
        result.append(f"{round(years)} years")
    if months:
        result.append(f"{round(months)} months")
    if days:
        result.append(f"{round(days)} days")
    if hours:
        result.append(f"{round(hours)} hrs")
    if minutes:
        result.append(f"{round(minutes)} mins")
    if seconds:
        result.append(f"{round(seconds)} secs")
    if milliseconds:
        result.append(f"{round(milliseconds * 1000)} msecs")
    return " ".join(result)
