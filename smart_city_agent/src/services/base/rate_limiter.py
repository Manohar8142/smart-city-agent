"""
Rate limiter using token bucket algorithm.

CONCEPT: Token Bucket Algorithm
- Imagine a bucket with tokens
- Bucket refills at constant rate (e.g., 60 tokens/minute)
- Each API call consumes 1 token
- If bucket empty, wait for refill
- Prevents exceeding API rate limits

CONCEPT: Why rate limiting?
- APIs have limits (e.g., 60 requests/minute)
- Exceeding limit → 429 Too Many Requests error
- Rate limiter prevents this proactively
"""

import asyncio
import time
from dataclasses import dataclass
from ...utils.logging import logger


@dataclass
class RateLimitConfig:
    """Rate limiter configuration"""

    max_requests: int  # Max tokens in bucket
    time_window: float  # Refill window in seconds


class TokenBucketRateLimiter:
    """
    Token bucket rate limiter.

    Example: 60 requests per minute
    - Bucket capacity: 60 tokens
    - Refill rate: 1 token/second
    """

    def __init__(self, max_requests: int, time_window: float):
        """
        Initialize rate limiter.

        Args:
            max_requests: Max requests allowed in time window
            time_window: Time window in seconds

        Example:
            # 60 requests per minute
            limiter = TokenBucketRateLimiter(60, 60.0)
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.tokens = float(max_requests)  # Start with full bucket
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()  # Thread-safe token updates

        # CONCEPT: Refill rate calculation
        # If 60 requests/60 seconds → 1 request/second
        self.refill_rate = max_requests / time_window

        logger.debug(
            f"Rate limiter initialized: {max_requests} requests per "
            f"{time_window}s (refill: {self.refill_rate:.2f}/s)"
        )

    async def acquire(self):
        """
        Acquire a token from the bucket.

        CONCEPT: Token acquisition process
        1. Calculate tokens to add since last refill
        2. Refill bucket (up to max capacity)
        3. If tokens available, consume one
        4. If no tokens, wait for refill

        This method blocks until a token is available.
        """
        async with self._lock:
            while True:
                now = time.monotonic()
                time_passed = now - self.last_refill

                # CONCEPT: Refill tokens based on time passed
                # tokens_to_add = refill_rate * time_passed
                # e.g., 1 token/sec * 5 seconds = 5 tokens
                tokens_to_add = self.refill_rate * time_passed
                self.tokens = min(self.max_requests, self.tokens + tokens_to_add)
                self.last_refill = now

                if self.tokens >= 1.0:
                    # Token available, consume it
                    self.tokens -= 1.0
                    logger.debug(f"Token acquired. Remaining: {self.tokens:.1f}")
                    return
                else:
                    # CONCEPT: Calculate wait time for next token
                    # wait_time = (1 - current_tokens) / refill_rate
                    wait_time = (1.0 - self.tokens) / self.refill_rate
                    logger.debug(f"Rate limit reached. Waiting {wait_time:.2f}s")
                    await asyncio.sleep(wait_time)

    def get_available_tokens(self) -> float:
        """Get current number of available tokens (for monitoring)"""
        now = time.monotonic()
        time_passed = now - self.last_refill
        tokens_to_add = self.refill_rate * time_passed
        return min(self.max_requests, self.tokens + tokens_to_add)
