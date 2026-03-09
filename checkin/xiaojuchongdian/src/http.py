"""HTTP client with retry for Xiaoju API-driven tasks."""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Dict

from .config import HttpConfig

if TYPE_CHECKING:
    import requests

logger = logging.getLogger(__name__)


class HttpClientError(RuntimeError):
    """Base exception for HTTP client errors."""


class AuthError(HttpClientError):
    """Raised when authentication is invalid or expired."""


class HttpStatusError(HttpClientError):
    """Raised on non-success HTTP status after retry."""


@dataclass(frozen=True)
class HttpResponse:
    status_code: int
    headers: Dict[str, str]
    data: Dict[str, Any]


class HttpClient:
    """Thin JSON HTTP wrapper with retry/backoff support."""

    RETRYABLE_STATUS = {429, 500, 502, 503, 504}
    AUTH_STATUS = {401, 403}

    def __init__(self, config: HttpConfig) -> None:
        self.config = config
        try:
            import requests as requests_module
        except ModuleNotFoundError as exc:
            raise HttpClientError(
                "missing dependency: requests. install via `python3 -m pip install requests`"
            ) from exc
        self._requests = requests_module
        self.session = self._requests.Session()

    def close(self) -> None:
        self.session.close()

    def __enter__(self) -> "HttpClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def post_json(self, url: str, body: Dict[str, Any], headers: Dict[str, str]) -> HttpResponse:
        last_error: Exception | None = None
        max_attempts = max(self.config.retries, 0) + 1
        for attempt in range(1, max_attempts + 1):
            try:
                response = self.session.post(
                    url,
                    json=body,
                    headers=headers,
                    timeout=self.config.timeout_seconds,
                )
            except self._requests.RequestException as exc:
                last_error = exc
                if attempt >= max_attempts:
                    raise HttpClientError(f"request failed after {attempt} attempts: {url}") from exc
                delay = self._backoff_delay(attempt)
                logger.warning(
                    "request to %s failed on attempt %d/%d (%s), retrying in %.1fs",
                    url, attempt, max_attempts, exc, delay,
                )
                self._sleep_before_retry(attempt)
                continue

            if response.status_code in self.AUTH_STATUS:
                raise AuthError(f"authentication failed: HTTP {response.status_code} for {url}")

            if response.status_code in self.RETRYABLE_STATUS:
                last_error = HttpStatusError(
                    f"retryable status HTTP {response.status_code} for {url}: {self._short_body(response.text)}"
                )
                if attempt >= max_attempts:
                    raise last_error
                delay = self._backoff_delay(attempt)
                logger.warning(
                    "retryable HTTP %d from %s on attempt %d/%d, retrying in %.1fs",
                    response.status_code, url, attempt, max_attempts, delay,
                )
                self._sleep_before_retry(attempt)
                continue

            if response.status_code >= 400:
                raise HttpStatusError(
                    f"http {response.status_code} for {url}: {self._short_body(response.text)}"
                )

            try:
                payload = response.json()
            except json.JSONDecodeError as exc:
                raise HttpClientError(
                    f"response is not valid json for {url}: {self._short_body(response.text)}"
                ) from exc

            if not isinstance(payload, dict):
                raise HttpClientError(
                    f"expected JSON object from {url}, got {type(payload).__name__}: "
                    f"{self._short_body(response.text)}"
                )

            return HttpResponse(
                status_code=response.status_code,
                headers=dict(response.headers),
                data=payload,
            )

        raise HttpClientError(f"request failed unexpectedly: {url}, last_error={last_error!r}")

    def _backoff_delay(self, attempt: int) -> float:
        return self.config.backoff_seconds * (self.config.backoff_factor ** max(attempt - 1, 0))

    def _sleep_before_retry(self, attempt: int) -> None:
        time.sleep(max(self._backoff_delay(attempt), 0.0))

    @staticmethod
    def _short_body(text: str, limit: int = 200) -> str:
        if len(text) <= limit:
            return text
        return text[:limit] + "..."
