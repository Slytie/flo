import datetime
from datetime import timezone

def timestamp():
    now = datetime.datetime.now(timezone.utc)
    ts = now.strftime("%Y-%m-%d-%H-%M-%S")
    return ts
