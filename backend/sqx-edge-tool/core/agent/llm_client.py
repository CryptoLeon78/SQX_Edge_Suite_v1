from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class OllamaConfig:
    base_url: str = "http://127.0.0.1:11434"
    model: str = "qwen3.5:latest"
    fallback_model: str = "qwen2.5-coder:3b"
    timeout_seconds: float = 12.0
    offline_only: bool = True
    auto_start: bool = True
    executable: str = ""
    startup_wait_seconds: float = 6.0


class OllamaClient:
    def __init__(self, config: OllamaConfig):
        self.config = config

    def _url(self, path: str) -> str:
        return self.config.base_url.rstrip("/") + "/" + path.lstrip("/")

    def _resolve_executable(self) -> str:
        configured = str(self.config.executable or "").strip()
        candidates = [
            configured,
            shutil.which("ollama") or "",
            str(Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Ollama" / "ollama.exe"),
            str(Path.home() / "AppData" / "Local" / "Programs" / "Ollama" / "ollama.exe"),
        ]
        for candidate in candidates:
            if candidate and Path(candidate).is_file():
                return candidate
        return ""

    def ensure_running(self) -> dict[str, Any]:
        if self.status(auto_start=False).get("available"):
            return {"started": False, "reason": "already_available"}
        if not self.config.auto_start:
            return {"started": False, "reason": "auto_start_disabled"}
        executable = self._resolve_executable()
        if not executable:
            return {"started": False, "reason": "ollama_executable_missing"}
        try:
            creationflags = 0
            startupinfo = None
            if os.name == "nt":
                creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.Popen(
                [executable, "serve"],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=creationflags,
                startupinfo=startupinfo,
            )
            deadline = time.monotonic() + max(0.5, self.config.startup_wait_seconds)
            while time.monotonic() < deadline:
                time.sleep(0.35)
                if self.status(auto_start=False).get("available"):
                    return {"started": True, "reason": "ollama_started", "executableFound": True}
            return {"started": True, "reason": "ollama_start_pending", "executableFound": True}
        except OSError as exc:
            return {"started": False, "reason": type(exc).__name__, "executableFound": True}

    def _json_request(self, path: str, payload: dict[str, Any] | None = None, *, method: str = "POST") -> dict[str, Any]:
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            self._url(path),
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=self.config.timeout_seconds) as response:
            body = response.read().decode("utf-8", errors="replace")
        return json.loads(body or "{}")

    def status(self, *, auto_start: bool | None = None) -> dict[str, Any]:
        try:
            tags = self._json_request("/api/tags", None, method="GET")
            models = [str(item.get("name") or "") for item in tags.get("models", []) if isinstance(item, dict)]
            selected = self.config.model if self.config.model in models else self.config.fallback_model
            return {
                "ok": True,
                "available": True,
                "model": selected,
                "configuredModel": self.config.model,
                "fallbackModel": self.config.fallback_model,
                "models": models,
                "autoStart": {"enabled": self.config.auto_start, "attempted": False, "started": False},
            }
        except (OSError, urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
            should_start = self.config.auto_start if auto_start is None else bool(auto_start)
            if should_start:
                start = self.ensure_running()
                if start.get("started") or start.get("reason") == "already_available":
                    retry = self.status(auto_start=False)
                    retry["autoStart"] = {"enabled": self.config.auto_start, "attempted": True, **start}
                    return retry
                start_reason = str(start.get("reason") or "status_failed")
            else:
                start_reason = "status_failed"
            return {
                "ok": False,
                "available": False,
                "model": self.config.model,
                "configuredModel": self.config.model,
                "fallbackModel": self.config.fallback_model,
                "error": type(exc).__name__,
                "autoStart": {
                    "enabled": self.config.auto_start,
                    "attempted": should_start,
                    "started": False,
                    "reason": start_reason,
                },
            }

    def chat_json(self, *, messages: list[dict[str, str]], schema: dict[str, Any], model: str | None = None) -> dict[str, Any]:
        selected = model or self.status().get("model") or self.config.model
        payload = {
            "model": selected,
            "messages": messages,
            "stream": False,
            "format": schema,
            "options": {"temperature": 0},
        }
        result = self._json_request("/api/chat", payload)
        content = ((result.get("message") or {}).get("content") or "").strip()
        return json.loads(content)

    def chat_text(
        self,
        *,
        messages: list[dict[str, str]],
        model: str | None = None,
        temperature: float = 0.1,
        num_predict: int | None = None,
    ) -> str:
        selected = model or self.status().get("model") or self.config.model
        options: dict[str, Any] = {"temperature": temperature}
        if num_predict is not None:
            options["num_predict"] = int(num_predict)
        payload = {
            "model": selected,
            "messages": messages,
            "stream": False,
            "options": options,
        }
        result = self._json_request("/api/chat", payload)
        return str(((result.get("message") or {}).get("content") or "")).strip()
