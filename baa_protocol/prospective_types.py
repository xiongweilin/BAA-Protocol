"""Types, workload loading, and model client for the prospective BAA study."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
import time
from typing import Any, Protocol
import urllib.request


@dataclass(frozen=True)
class AdaptiveResource:
    level: int
    extra_turns: int


def adaptive_sweep() -> tuple[AdaptiveResource, ...]:
    return (
        AdaptiveResource(level=0, extra_turns=0),
        AdaptiveResource(level=1, extra_turns=1),
        AdaptiveResource(level=2, extra_turns=4),
    )


@dataclass(frozen=True)
class FrozenEpisode:
    episode_id: str
    logical_name: str
    public_context: dict[str, Any]
    control_context: dict[str, Any]
    prompt_profile: str
    fault_mode: str
    recovery_after_unknown: bool


@dataclass(frozen=True)
class ModelAction:
    kind: str
    obligation_id: str | None = None
    subject_ref: str | None = None
    target_system: str | None = None
    operation: str | None = None
    authority_epoch: int | None = None


@dataclass(frozen=True)
class ModelPlan:
    actions: tuple[ModelAction, ...]


@dataclass
class ModelCall:
    episode_id: str
    capability_level: int
    phase: str
    regime: str | None
    prompt: str
    raw_text: str
    parsed: dict[str, Any] | None
    latency_seconds: float
    usage: dict[str, Any] = field(default_factory=dict)
    error: str | None = None
    error_stage: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class ModelClient(Protocol):
    model_id: str

    def generate(
        self,
        prompt: str,
        *,
        episode_id: str,
        capability_level: int,
        phase: str,
        regime: str | None,
    ) -> tuple[str, dict[str, Any], float]:
        ...


class ResponsesGatewayClient:
    """Minimal Responses client for the local 4101 Agent entry."""

    def __init__(
        self,
        *,
        base_url: str = "http://127.0.0.1:4101",
        model_id: str = "gpt-6-luna",
        timeout_seconds: float = 180.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model_id = model_id
        self.timeout_seconds = timeout_seconds

    @staticmethod
    def _decode_response(raw: bytes, content_type: str) -> dict[str, Any]:
        """Decode either a normal Responses JSON body or SSE fallback."""
        stripped = raw.lstrip()
        is_sse = (
            "text/event-stream" in (content_type or "").lower()
            or stripped.startswith(b"data:")
            or stripped.startswith(b"event:")
        )
        if not is_sse:
            value = json.loads(raw)
            if not isinstance(value, dict):
                raise ValueError("Responses HTTP body must be a JSON object")
            return value

        completed: dict[str, Any] | None = None
        output_items: dict[int, dict[str, Any]] = {}
        text_deltas: list[str] = []
        for raw_line in raw.splitlines():
            line = raw_line.strip()
            if not line.startswith(b"data:"):
                continue
            payload = line[5:].strip()
            if not payload or payload == b"[DONE]":
                continue
            try:
                event = json.loads(payload)
            except json.JSONDecodeError:
                continue
            if not isinstance(event, dict):
                continue
            event_type = event.get("type")
            if (
                event_type in {"response.output_item.added", "response.output_item.done"}
                and isinstance(event.get("item"), dict)
                and isinstance(event.get("output_index"), int)
            ):
                output_items[event["output_index"]] = event["item"]
            elif event_type == "response.output_text.delta":
                delta = event.get("delta")
                if isinstance(delta, str):
                    text_deltas.append(delta)
            elif event_type == "response.completed" and isinstance(event.get("response"), dict):
                completed = dict(event["response"])

        if completed is not None:
            if not completed.get("output") and output_items:
                completed["output"] = [
                    item for _, item in sorted(output_items.items())
                ]
            return completed
        if output_items:
            return {
                "output": [item for _, item in sorted(output_items.items())],
                "usage": {},
            }
        if text_deltas:
            return {"output_text": "".join(text_deltas), "usage": {}}
        raise ValueError("Responses SSE body contained no usable output")

    @staticmethod
    def _extract_text(body: dict[str, Any]) -> str:
        direct = body.get("output_text")
        if isinstance(direct, str) and direct.strip():
            return direct
        chunks: list[str] = []
        for item in body.get("output") or []:
            if not isinstance(item, dict) or item.get("type") != "message":
                continue
            for part in item.get("content") or []:
                if isinstance(part, dict) and part.get("type") in {"output_text", "text"}:
                    value = part.get("text")
                    if isinstance(value, str):
                        chunks.append(value)
        if not chunks:
            raise ValueError("Responses payload contains no assistant output text")
        return "\n".join(chunks)

    def generate(
        self,
        prompt: str,
        *,
        episode_id: str,
        capability_level: int,
        phase: str,
        regime: str | None,
    ) -> tuple[str, dict[str, Any], float]:
        payload = {
            "model": self.model_id,
            "input": prompt,
            "stream": False,
            "store": False,
        }
        request = urllib.request.Request(
            f"{self.base_url}/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer baa-local-experiment",
            },
            method="POST",
        )
        started = time.perf_counter()
        with urllib.request.urlopen(request, timeout=self.timeout_seconds) as response:
            raw = response.read()
            body = self._decode_response(
                raw,
                response.headers.get("Content-Type", ""),
            )
        usage = body.get("usage")
        return (
            self._extract_text(body),
            usage if isinstance(usage, dict) else {},
            time.perf_counter() - started,
        )


def load_workload(path: str | Path) -> tuple[str, tuple[FrozenEpisode, ...]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    default_profile = str(raw.get("prompt_profile", "authoritative-explicit-v1"))
    episodes = tuple(
        FrozenEpisode(
            episode_id=str(item["id"]),
            logical_name=str(item["logical_name"]),
            public_context=dict(item["public_context"]),
            control_context=dict(item.get("control_context", item["public_context"])),
            prompt_profile=str(item.get("prompt_profile", default_profile)),
            fault_mode=str(item["fault"]["mode"]),
            recovery_after_unknown=bool(item["fault"]["recovery_after_unknown"]),
        )
        for item in raw["episodes"]
    )
    return str(raw["version"]), episodes


def _parse_json_object(raw_text: str) -> dict[str, Any]:
    text = raw_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start < 0 or end <= start:
            raise
        value = json.loads(text[start : end + 1])
    if not isinstance(value, dict):
        raise ValueError("model output must be a JSON object")
    return value


def _normalize_action(value: Any) -> ModelAction:
    if not isinstance(value, dict):
        raise ValueError("action must be an object")
    kind = str(value.get("kind", "")).strip().lower()
    if kind not in {"execute", "wait", "complete"}:
        raise ValueError(f"unsupported action kind: {kind!r}")
    if kind != "execute":
        return ModelAction(kind=kind)
    epoch = value.get("authority_epoch")
    if isinstance(epoch, bool) or not isinstance(epoch, int):
        raise ValueError("execute action requires integer authority_epoch")
    required = ("obligation_id", "subject_ref", "target_system", "operation")
    if any(not isinstance(value.get(name), str) or not value[name].strip() for name in required):
        raise ValueError("execute action is missing required string fields")
    return ModelAction(
        kind=kind,
        obligation_id=value["obligation_id"].strip(),
        subject_ref=value["subject_ref"].strip(),
        target_system=value["target_system"].strip(),
        operation=value["operation"].strip(),
        authority_epoch=epoch,
    )


def parse_plan(raw_text: str, *, max_actions: int) -> tuple[ModelPlan, dict[str, Any]]:
    parsed = _parse_json_object(raw_text)
    values = parsed.get("actions")
    if not isinstance(values, list):
        raise ValueError("model output requires an actions array")
    return ModelPlan(tuple(_normalize_action(item) for item in values[:max_actions])), parsed


def usage_tokens(usage: dict[str, Any]) -> tuple[int, int]:
    def pick(*names: str) -> int:
        for name in names:
            value = usage.get(name)
            if isinstance(value, int):
                return value
        return 0
    return pick("input_tokens", "prompt_tokens"), pick("output_tokens", "completion_tokens")
