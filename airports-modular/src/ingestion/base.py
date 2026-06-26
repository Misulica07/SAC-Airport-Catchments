"""Shared interface for every ingestion source.

Subclasses implement :meth:`fetch` and :meth:`save`; the base class provides
common retry-with-backoff, environment-variable plumbing, and logging.
"""

from __future__ import annotations

import os
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

import requests

from src.utils.logging import get_logger


class BaseIngester(ABC):
    """Abstract ingester. One subclass per upstream data source."""

    #: Environment variable name to read for the API key. ``None`` if the
    #: source is unauthenticated (e.g. the ONS Geoportal).
    api_key_env: str | None = None

    def __init__(
        self,
        output_dir: str | Path,
        retry_attempts: int = 3,
        retry_backoff_seconds: int = 5,
        timeout_seconds: int = 30,
    ) -> None:
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.retry_attempts = retry_attempts
        self.retry_backoff_seconds = retry_backoff_seconds
        self.timeout_seconds = timeout_seconds
        self.log = get_logger(self.__class__.__name__)

        self.api_key = self._read_api_key()

    # ------------------------------------------------------------------
    # Subclass hooks
    # ------------------------------------------------------------------

    @abstractmethod
    def fetch(self, *args: Any, **kwargs: Any) -> Any:
        """Pull a single record from the upstream source."""

    @abstractmethod
    def save(self, payload: Any, name: str) -> Path:
        """Persist a record under :attr:`output_dir`. Return the file path."""

    # ------------------------------------------------------------------
    # Shared helpers
    # ------------------------------------------------------------------

    def _read_api_key(self) -> str | None:
        if not self.api_key_env:
            return None
        key = os.environ.get(self.api_key_env, "").strip()
        if not key:
            raise RuntimeError(
                f"Missing {self.api_key_env}. Copy .env.example to .env and add it."
            )
        return key

    def _post_with_retry(
        self,
        url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],
    ) -> dict[str, Any]:
        """POST with exponential backoff. Raises on final failure."""
        last_exc: Exception | None = None
        for attempt in range(1, self.retry_attempts + 1):
            try:
                resp = requests.post(
                    url, json=json, headers=headers, timeout=self.timeout_seconds
                )
                resp.raise_for_status()
                return resp.json()
            except requests.RequestException as exc:
                last_exc = exc
                wait = self.retry_backoff_seconds * attempt
                self.log.warning(
                    "POST %s failed (attempt %d/%d): %s — retrying in %ds",
                    url,
                    attempt,
                    self.retry_attempts,
                    exc,
                    wait,
                )
                time.sleep(wait)

        raise RuntimeError(
            f"POST {url} failed after {self.retry_attempts} attempts"
        ) from last_exc
