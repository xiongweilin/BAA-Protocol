"""Replay-safe client transport recovery for qualified prospective studies."""

from __future__ import annotations

import http.client
import json
import time
import urllib.error
from typing import Any

from .prospective_types import ModelResponseError


class ReplaySafeTransportClient:
    """Retry only failures that occur before a usable model response exists.

    This wrapper is intentionally narrower than a generic retry policy. Explicit
    HTTP status failures and model-level response failures are not retried. The
    caller therefore cannot turn a refusal, missing function call, or other
    model/interface failure into a different sample by retrying it.
    """

    def __init__(self, client: Any, *, max_retries: int = 1) -> None:
        if max_retries < 0:
            raise ValueError("max_retries must be non-negative")
        self.client = client
        self.max_retries = max_retries
        self.model_id = client.model_id
        self.interface_mode = getattr(client, "interface_mode", "unspecified")
        self.http_attempts = 0
        self.transport_failures_seen = 0
        self.transport_retries = 0
        self.recovered_transport_calls = 0

    @staticmethod
    def _retryable(exc: Exception) -> bool:
        # HTTPError is also a URLError, but an explicit HTTP response is already
        # an observed result and must not be silently converted into a new sample.
        if isinstance(exc, urllib.error.HTTPError):
            return False
        if isinstance(exc, ModelResponseError):
            return False
        return isinstance(
            exc,
            (
                urllib.error.URLError,
                http.client.IncompleteRead,
                ConnectionError,
                TimeoutError,
                json.JSONDecodeError,
                ValueError,
            ),
        )

    def generate(
        self,
        prompt: str,
        *,
        episode_id: str,
        capability_level: int,
        phase: str,
        regime: str | None,
    ):
        retried = False
        for attempt in range(self.max_retries + 1):
            self.http_attempts += 1
            try:
                result = self.client.generate(
                    prompt,
                    episode_id=episode_id,
                    capability_level=capability_level,
                    phase=phase,
                    regime=regime,
                )
            except Exception as exc:
                if not self._retryable(exc):
                    raise
                self.transport_failures_seen += 1
                if attempt >= self.max_retries:
                    raise
                self.transport_retries += 1
                retried = True
                time.sleep(0.25 * (attempt + 1))
                continue

            if retried:
                self.recovered_transport_calls += 1
            return result

        raise AssertionError("unreachable transport retry state")
