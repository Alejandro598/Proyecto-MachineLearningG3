import pandas as pd
from datetime import datetime

def format_datetime_for_display(dt_str: str) -> str:
    if dt_str:
        return pd.to_datetime(dt_str).strftime('%Y-%m-%d %H:%M')
    return ""
