from collections import defaultdict
from datetime import datetime, timedelta

from fastapi import HTTPException


class RateLimiter:

    def __init__(self):

        self.storage = defaultdict(list)

    def allow(self, key: str, limit: int, window_seconds: int):

        now = datetime.utcnow()

        window_start = now - timedelta(seconds=window_seconds)

        requests = self.storage[key]

        requests[:] = [timestamp for timestamp in requests if timestamp > window_start]

        if len(requests) >= limit:

            raise HTTPException(
                status_code=429, detail="Too many requests. Please try again later."
            )

        requests.append(now)


rate_limiter = RateLimiter()
