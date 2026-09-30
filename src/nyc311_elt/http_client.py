

import httpx
import time
import random
import logging

logger = logging.getLogger(__name__)

def compute_backoff(attempt: int, base: float, cap: float) -> float:
    max_time = min(cap, base * (2 ** attempt))
    return random.uniform(0, max_time)

def get_with_retries(
    client: httpx.Client,
    url: str,
    params: dict[str, str | int],
    *,
    max_retries: int = 5,
    backoff_base: float = 1.0,
    backoff_cap: float = 30.0,
    retryable_status: frozenset[int] = frozenset({429, 500, 502, 503, 504}),
) -> list[dict]:

    for attempt in range(max_retries + 1):
        is_last_attempt = attempt == max_retries
        try:
            response = client.get(url, params=params)
        except httpx.TransportError as e:
            
            if is_last_attempt:
                raise
            wait = compute_backoff(attempt, backoff_base, backoff_cap)
            logger.warning(f"Attempt {attempt + 1} failed with error: {type(e).__name__}. Retrying in {wait:.2f} seconds...")
            time.sleep(wait)
            continue  
        if response.is_success:
            return response.json()
        if response.status_code not in retryable_status:
            raise httpx.HTTPStatusError(
                f"Request failed with status code {response.status_code}",
                request=response.request,
                response=response,
            )
        if is_last_attempt:
            raise httpx.HTTPStatusError(
                f"Request failed with status code {response.status_code} after {max_retries+1} attempts",
                request=response.request,
                response=response,
            )

        wait = compute_backoff(attempt, backoff_base, backoff_cap)
        logger.warning(f"Attempt {attempt + 1} failed with status code {response.status_code}. Retrying in {wait:.2f} seconds...") 
        time.sleep(wait)
    
