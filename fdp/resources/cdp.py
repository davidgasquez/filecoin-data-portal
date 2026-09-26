import datetime as dt
import logging
import random
import time
from email.utils import parsedate_to_datetime

import httpx

logger = logging.getLogger(__name__)
MAX_ATTEMPTS = 4
MAX_DELAY = 60.0
RETRYABLE_STATUSES = {429, 500, 502, 503, 504}


def retry_delay(response: httpx.Response | None, attempt: int) -> float:
    delay = 2**attempt + random.uniform(0, 1)
    value = response.headers.get("Retry-After") if response is not None else None
    if value:
        try:
            seconds = float(int(value))
        except ValueError:
            try:
                seconds = (
                    parsedate_to_datetime(value) - dt.datetime.now(dt.UTC)
                ).total_seconds()
            except TypeError, ValueError, OverflowError:
                seconds = 0
        delay = max(delay, seconds)
    return min(delay, MAX_DELAY)


def get_json(url: str):
    """Fetch a CDP snapshot, retrying only transient request failures."""
    with httpx.Client(follow_redirects=True, timeout=60) as client:
        for attempt in range(1, MAX_ATTEMPTS + 1):
            response = None
            try:
                response = client.get(url)
                response.raise_for_status()
            except (
                httpx.TimeoutException,
                httpx.NetworkError,
                httpx.HTTPStatusError,
            ) as exc:
                if isinstance(exc, httpx.HTTPStatusError) and (
                    exc.response.status_code not in RETRYABLE_STATUSES
                ):
                    raise
                reason = (
                    f"HTTP {response.status_code}"
                    if response is not None
                    else type(exc).__name__
                )
                if attempt == MAX_ATTEMPTS:
                    logger.error(
                        "CDP %s failed: %s (attempt %s/%s)",
                        url,
                        reason,
                        attempt,
                        MAX_ATTEMPTS,
                    )
                    raise
                delay = retry_delay(response, attempt)
                logger.warning(
                    "CDP %s failed: %s (attempt %s/%s); retrying in %.1fs",
                    url,
                    reason,
                    attempt,
                    MAX_ATTEMPTS,
                    delay,
                )
                time.sleep(delay)
            else:
                return response.json()
    raise AssertionError("Unreachable retry state")
