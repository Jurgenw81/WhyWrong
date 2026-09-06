from __future__ import annotations

from collections import defaultdict, deque
from time import monotonic
from typing import Callable


class SlidingWindowRateLimiter:
    """Process-local limiter for the small public hackathon demo."""

    def __init__(
        self,
        limit: int,
        window_seconds: int,
        *,
        clock: Callable[[], float] = monotonic,
    ) -> None:
        if limit < 1 or window_seconds < 1:
            raise ValueError("Rate limit and window must be positive")
        self.limit = limit
        self.window_seconds = window_seconds
        self.clock = clock
        self._requests: dict[str, deque[float]] = defaultdict(deque)

    def allow(self, key: str) -> tuple[bool, int]:
        now = self.clock()
        cutoff = now - self.window_seconds
        requests = self._requests[key]
        while requests and requests[0] <= cutoff:
            requests.popleft()
        if len(requests) >= self.limit:
            retry_after = max(1, int(requests[0] + self.window_seconds - now) + 1)
            return False, retry_after
        requests.append(now)
        return True, 0

    def clear(self) -> None:
        self._requests.clear()

