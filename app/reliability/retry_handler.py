"""
Retry Handler — Exponential Backoff with Jitter
================================================
Provides a reusable decorator for retrying failed function calls
with exponential backoff and optional jitter to prevent thundering herd.

Works with both regular (sync) and async functions.

Usage:
    from app.reliability.retry_handler import with_retry

    # On a sync function:
    @with_retry(max_retries=3, base_delay=0.5)
    def call_external_service():
        ...

    # On an async function:
    @with_retry(max_retries=3, base_delay=1.0, exceptions=(ConnectionError,))
    async def call_llm(prompt: str) -> str:
        ...
"""

import asyncio
import functools
import random
import time
from dataclasses import dataclass, field
from typing import Callable, Tuple, Type

from app.observability.logging import logger


@dataclass
class RetryConfig:
    """
    Configuration for the retry decorator.

    Attributes:
        max_retries:    Maximum number of retry attempts after the first failure.
        base_delay:     Initial wait time in seconds before the first retry.
        max_delay:      Upper bound on wait time between retries (seconds).
        backoff_factor: Multiplier applied to delay after each failed attempt.
                        delay = base_delay * (backoff_factor ** attempt)
        jitter:         If True, adds a small random offset to each delay to
                        avoid the thundering herd problem (multiple clients
                        retrying at exactly the same moment).
        exceptions:     Tuple of exception types that should trigger a retry.
                        Any other exception will propagate immediately.
    """
    max_retries: int = 3
    base_delay: float = 0.5
    max_delay: float = 10.0
    backoff_factor: float = 2.0
    jitter: bool = True
    exceptions: Tuple[Type[Exception], ...] = field(
        default_factory=lambda: (Exception,)
    )


def _compute_delay(config: RetryConfig, attempt: int) -> float:
    """
    Calculate the wait time before the next retry attempt.

    Formula:
        delay = min(base_delay * (backoff_factor ** attempt), max_delay)

    If jitter is enabled, a random offset of ±20% is added to prevent
    multiple clients from retrying at the exact same moment (thundering herd).

    Args:
        config:  The retry configuration object.
        attempt: The current attempt index (0-based).

    Returns:
        The number of seconds to wait before the next retry.
    """
    delay = min(
        config.base_delay * (config.backoff_factor ** attempt),
        config.max_delay
    )

    if config.jitter:
        # Add a random offset of up to ±20% of the computed delay.
        jitter_range = delay * 0.2
        delay += random.uniform(-jitter_range, jitter_range)

    # Ensure delay is never negative (can happen with large negative jitter)
    return max(delay, 0.0)


def with_retry(
    max_retries: int = 3,
    base_delay: float = 0.5,
    max_delay: float = 10.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
) -> Callable:
    """
    Decorator factory that wraps a function with retry logic.

    Automatically detects whether the wrapped function is async or sync
    and applies the correct retry mechanism.

    Args:
        max_retries:    How many times to retry on failure (default: 3).
        base_delay:     Initial delay in seconds before first retry (default: 0.5).
        max_delay:      Maximum delay cap in seconds (default: 10.0).
        backoff_factor: Multiplier for delay growth between retries (default: 2.0).
        jitter:         Add randomness to delay to avoid thundering herd (default: True).
        exceptions:     Exception types to retry on (default: all exceptions).

    Returns:
        A decorator that wraps the target function with retry behaviour.

    Example:
        @with_retry(max_retries=3, base_delay=1.0, exceptions=(ConnectionError, TimeoutError))
        async def call_ollama(prompt: str) -> str:
            ...
    """
    config = RetryConfig(
        max_retries=max_retries,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_factor=backoff_factor,
        jitter=jitter,
        exceptions=exceptions,
    )

    def decorator(func: Callable) -> Callable:

        if asyncio.iscoroutinefunction(func):
            # ── Async version ──────────────────────────────────────────────
            @functools.wraps(func)
            async def async_wrapper(*args, **kwargs):
                last_exception: Exception = Exception("Unknown error")

                for attempt in range(config.max_retries + 1):
                    try:
                        return await func(*args, **kwargs)

                    except config.exceptions as exc:
                        last_exception = exc

                        if attempt == config.max_retries:
                            # All retries exhausted — log and raise final error
                            logger.error(
                                f"[retry] '{func.__name__}' failed after "
                                f"{config.max_retries + 1} attempts. "
                                f"Final error: {exc}"
                            )
                            raise

                        delay = _compute_delay(config, attempt)
                        logger.warning(
                            f"[retry] '{func.__name__}' failed on attempt "
                            f"{attempt + 1}/{config.max_retries + 1}. "
                            f"Retrying in {delay:.2f}s. Error: {exc}"
                        )
                        await asyncio.sleep(delay)

                raise last_exception  # unreachable, but satisfies type checker

            return async_wrapper

        else:
            # ── Sync version ───────────────────────────────────────────────
            @functools.wraps(func)
            def sync_wrapper(*args, **kwargs):
                last_exception: Exception = Exception("Unknown error")

                for attempt in range(config.max_retries + 1):
                    try:
                        return func(*args, **kwargs)

                    except config.exceptions as exc:
                        last_exception = exc

                        if attempt == config.max_retries:
                            logger.error(
                                f"[retry] '{func.__name__}' failed after "
                                f"{config.max_retries + 1} attempts. "
                                f"Final error: {exc}"
                            )
                            raise

                        delay = _compute_delay(config, attempt)
                        logger.warning(
                            f"[retry] '{func.__name__}' failed on attempt "
                            f"{attempt + 1}/{config.max_retries + 1}. "
                            f"Retrying in {delay:.2f}s. Error: {exc}"
                        )
                        time.sleep(delay)

                raise last_exception  # unreachable, but satisfies type checker

            return sync_wrapper

    return decorator
