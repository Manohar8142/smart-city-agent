"""
Base HTTP client with production patterns.

CONCEPT: Why a base client?
- Avoid code duplication across API clients
- Centralize retry logic, error handling, logging
- Connection pooling (reuse TCP connections for better performance)
- Consistent timeout and error handling

CONCEPT: Async/await
- Async enables concurrent I/O operations (multiple API calls at once)
- await pauses execution until async operation completes
- Event loop manages all async operations
"""

import httpx
from typing import Any, Dict, Optional
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
)
from ...utils.logging import logger
from ...utils.errors import ExternalAPIError


class BaseHTTPClient:
    """
    Base HTTP client using httpx with async support.

    CONCEPT: Why httpx over requests?
    - Async/await support (requests is sync-only)
    - HTTP/2 support for better performance
    - Connection pooling built-in
    - Same API as requests (easy migration)
    """

    def __init__(
        self,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 3,
        headers: Optional[Dict[str, str]] = None,
    ):
        """
        Initialize base HTTP client.

        Args:
            base_url: Base URL for API (e.g., "https://api.example.com")
            timeout: Request timeout in seconds
            max_retries: Max number of retry attempts
            headers: Default headers for all requests
        """
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.default_headers = headers or {}
        self.client: Optional[httpx.AsyncClient] = None

    async def __aenter__(self):
        """
        CONCEPT: Async context manager entry.
        - Called when entering 'async with' block
        - Initialize httpx.AsyncClient here
        - Client maintains connection pool for reuse
        """
        self.client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self.default_headers,
            follow_redirects=True,
        )
        logger.debug(f"Initialized HTTP client for {self.base_url}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """
        CONCEPT: Async context manager exit.
        - Called when exiting 'async with' block
        - Close connections gracefully
        - Release resources
        """
        if self.client:
            await self.client.aclose()
            logger.debug(f"Closed HTTP client for {self.base_url}")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.NetworkError)),
        reraise=True,
    )
    async def get(
        self,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        GET request with retry logic.

        CONCEPT: Exponential backoff
        - Try 1: Wait 2 seconds
        - Try 2: Wait 4 seconds
        - Try 3: Wait 8 seconds
        - Prevents overwhelming server during issues

        Args:
            endpoint: API endpoint (e.g., "/weather")
            params: Query parameters
            headers: Additional headers

        Returns:
            JSON response as dict

        Raises:
            ExternalAPIError: On API errors
        """
        if not self.client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        try:
            logger.debug(f"GET {endpoint} params={params}")

            response = await self.client.get(endpoint, params=params, headers=headers)

            # CONCEPT: HTTP status codes
            # 2xx: Success
            # 4xx: Client error (bad request, auth, not found)
            # 5xx: Server error (temporary, retry may work)
            response.raise_for_status()

            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise ExternalAPIError(
                f"API request failed: {e.response.status_code}",
                details={"url": str(e.request.url), "status": e.response.status_code},
            )
        except httpx.TimeoutException as e:
            logger.error(f"Request timeout: {e}")
            raise
        except httpx.NetworkError as e:
            logger.error(f"Network error: {e}")
            raise
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise ExternalAPIError(
                f"Unexpected API error: {str(e)}", details={"error": str(e)}
            )

    async def post(
        self,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        POST request with retry logic.

        Args:
            endpoint: API endpoint
            json: JSON body (for application/json)
            data: Form data (for application/x-www-form-urlencoded)
            headers: Additional headers

        Returns:
            JSON response as dict
        """
        if not self.client:
            raise RuntimeError(
                "Client not initialized. Use 'async with' context manager"
            )

        try:
            logger.debug(f"POST {endpoint}")

            response = await self.client.post(
                endpoint, json=json, data=data, headers=headers
            )

            response.raise_for_status()
            return response.json()

        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e}")
            raise ExternalAPIError(
                f"API request failed: {e.response.status_code}",
                details={"url": str(e.request.url), "status": e.response.status_code},
            )
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            raise ExternalAPIError(
                f"Unexpected API error: {str(e)}", details={"error": str(e)}
            )
