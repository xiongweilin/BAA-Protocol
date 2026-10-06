"""Structured progress telemetry for long-running real-model studies.

The wrapper is intentionally transparent: it proxies every model-client
attribute and only emits progress events around generate() calls. It does not
change prompts, retries, sampling, qualification, or result accounting.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import sys
import threading
import time
from typing import Any, TextIO


@dataclass
class _ProgressState:
    started_calls: int = 0
    completed_calls: int = 0
    failed_calls: int = 0
    current: dict[str, Any] | None = None


class ProgressModelClient:
    """Transparent model-client proxy with JSONL call progress and heartbeat."""

    def __init__(
        self,
        inner: Any,
        *,
        label: str,
        heartbeat_seconds: float = 30.0,
        stream: TextIO | None = None,
    ) -> None:
        if heartbeat_seconds <= 0:
            raise ValueError("heartbeat_seconds must be positive")
        self._inner = inner
        self._label = label
        self._heartbeat_seconds = heartbeat_seconds
        self._stream = stream or sys.stdout
        self._state = _ProgressState()
        self._lock = threading.Lock()
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self._started_at = 0.0

    def __getattr__(self, name: str) -> Any:
        return getattr(self._inner, name)

    def _emit(self, event: str, **extra: Any) -> None:
        with self._lock:
            payload = {
                "progress_event": event,
                "label": self._label,
                "elapsed_seconds": round(
                    max(0.0, time.monotonic() - self._started_at),
                    3,
                ),
                "started_calls": self._state.started_calls,
                "completed_calls": self._state.completed_calls,
                "failed_calls": self._state.failed_calls,
                "current": self._state.current,
                **extra,
            }
        print(json.dumps(payload, sort_keys=True), file=self._stream, flush=True)

    def _heartbeat(self) -> None:
        while not self._stop.wait(self._heartbeat_seconds):
            self._emit("heartbeat")

    def __enter__(self) -> "ProgressModelClient":
        self._started_at = time.monotonic()
        self._thread = threading.Thread(
            target=self._heartbeat,
            name=f"{self._label}-progress",
            daemon=True,
        )
        self._thread.start()
        self._emit("study_started")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=max(1.0, self._heartbeat_seconds * 2))
        self._emit("study_finished", error=None if exc is None else type(exc).__name__)

    def generate(self, prompt: str, **kwargs: Any):
        metadata = {
            key: kwargs.get(key)
            for key in ("episode_id", "capability_level", "phase", "regime")
            if key in kwargs
        }
        call_started = time.monotonic()
        with self._lock:
            self._state.started_calls += 1
            call_number = self._state.started_calls
            self._state.current = {
                "call_number": call_number,
                **metadata,
            }
        self._emit("model_call_started", call_number=call_number, **metadata)
        try:
            result = self._inner.generate(prompt, **kwargs)
        except Exception:
            with self._lock:
                self._state.failed_calls += 1
                self._state.current = None
            self._emit(
                "model_call_failed",
                call_number=call_number,
                call_elapsed_seconds=round(time.monotonic() - call_started, 3),
                **metadata,
            )
            raise
        with self._lock:
            self._state.completed_calls += 1
            self._state.current = None
        self._emit(
            "model_call_completed",
            call_number=call_number,
            call_elapsed_seconds=round(time.monotonic() - call_started, 3),
            **metadata,
        )
        return result
