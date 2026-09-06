import unittest

from backend.api.rate_limit import SlidingWindowRateLimiter


class MutableClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


class RateLimiterTests(unittest.TestCase):
    def test_blocks_after_limit_and_reports_retry(self) -> None:
        clock = MutableClock()
        limiter = SlidingWindowRateLimiter(2, 60, clock=clock)
        self.assertEqual(limiter.allow("student"), (True, 0))
        self.assertEqual(limiter.allow("student"), (True, 0))
        allowed, retry_after = limiter.allow("student")
        self.assertFalse(allowed)
        self.assertEqual(retry_after, 61)

    def test_window_expires_and_keys_are_independent(self) -> None:
        clock = MutableClock()
        limiter = SlidingWindowRateLimiter(1, 10, clock=clock)
        self.assertTrue(limiter.allow("student-a")[0])
        self.assertTrue(limiter.allow("student-b")[0])
        self.assertFalse(limiter.allow("student-a")[0])
        clock.now = 10
        self.assertTrue(limiter.allow("student-a")[0])


if __name__ == "__main__":
    unittest.main()
