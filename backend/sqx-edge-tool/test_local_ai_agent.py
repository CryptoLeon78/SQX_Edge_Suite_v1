import json
from unittest.mock import patch

from api import server
from core.agent.llm_client import OllamaClient, OllamaConfig
from core.agent.redaction import redact_data, redact_text
from core.agent.tool_catalog import build_action_catalog
from core.agent.policy import create_confirmation, consume_confirmation, is_action_allowed
from tools.build_sqx142_source_translator import patch_html


def test_agent_redaction_removes_sensitive_values():
    text = r"user@example.com abre https://app.sqxedgesuite.org/dashboard y C:\Users\Ivan SQX\secret con token=abcdefghi123456789"
    redacted = redact_text(text)
    assert "user@example.com" not in redacted
    assert "https://app.sqxedgesuite.org" not in redacted
    assert r"C:\Users\Ivan SQX" not in redacted
    assert "abcdefghi123456789" not in redacted

    data = redact_data({"email": "user@example.com", "output_path": r"C:\SQX\file.cfx", "safe": "ok"})
    assert data["email"] == "[REDACTED_EMAIL]"
    assert data["output_path"] == "[REDACTED_PATH]"
    assert data["safe"] == "ok"


def test_agent_policy_requires_confirmation_for_navigation():
    actions = build_action_catalog()
    action = actions["open_stage_tool:capa1-generate"]
    allowed, reason = is_action_allowed(action, confirmed=False)
    assert allowed is False
    assert reason == "agent_action_confirmation_required"

    confirmation = create_confirmation(action, {"stage": "capa1-generate"})
    ok, reason = consume_confirmation(confirmation["confirmation"]["token"], action.id)
    assert ok is True
    assert reason == "confirmed"


def test_agent_status_handles_ollama_unavailable_without_paths():
    client = server.app.test_client()
    with patch.object(server.OllamaClient, "status", return_value={
        "ok": False,
        "available": False,
        "model": "qwen3.5:latest",
        "configuredModel": "qwen3.5:latest",
        "fallbackModel": "qwen2.5-coder:3b",
        "error": "URLError",
    }), patch.object(server, "build_sqx142_status", return_value={
        "version": "sqx142-compat-status-v1",
        "ok": False,
        "status": "needs_hardening",
        "privacy": {"local_paths_returned": False},
    }), patch.object(server, "build_sqx142_performance_status", return_value={
        "version": "sqx142-performance-status-v1",
        "ok": False,
        "status": "warn",
        "activeProfile": {"id": "baseline_143_safe"},
        "privacy": {"local_paths_returned": False},
    }):
        response = client.get("/api/agent/status")
    data = response.get_json()
    raw = json.dumps(data, ensure_ascii=False)
    assert response.status_code == 200
    assert data["ok"] is True
    assert data["active"] is False
    assert data["provider"]["available"] is False
    assert data["sqx142Compat"]["status"] == "needs_hardening"
    assert data["sqx142Performance"]["activeProfile"]["id"] == "baseline_143_safe"
    assert data["privacy"]["local_paths_returned"] is False
    assert "C:\\" not in raw


def test_ollama_status_attempts_autostart_when_unavailable():
    client = OllamaClient(OllamaConfig(auto_start=True, startup_wait_seconds=0.1))
    with patch.object(client, "_json_request", side_effect=OSError("offline")), patch.object(client, "ensure_running", return_value={"started": False, "reason": "ollama_executable_missing"}):
        status = client.status()
    assert status["available"] is False
    assert status["autoStart"]["attempted"] is True
    assert status["autoStart"]["reason"] == "ollama_executable_missing"


def test_agent_endpoints_require_remote_app_session_for_tunnel_users():
    client = server.app.test_client()
    response = client.get(
        "/api/agent/status",
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    data = response.get_json()
    assert response.status_code == 403
    assert data["error"] == "remote_ai_session_required"
    assert data["privacy"]["raw_email_returned"] is False


def test_agent_status_allows_authenticated_remote_tester_session_without_monitor():
    client = server.app.test_client()
    session_status = {
        "session": {"active": True, "email_ref": "te***@example.invalid", "entitlement_kind": "tester_free"},
        "entitlement": {"kind": "tester_free", "status": "active"},
        "access": {"allowed": True, "feature_scope": "full"},
    }
    with patch.object(server, "_remote_session_status_for_request", return_value=(session_status, "device-1")), patch.object(server.OllamaClient, "status", return_value={
        "ok": True,
        "available": True,
        "model": "qwen3.5:latest",
        "configuredModel": "qwen3.5:latest",
        "fallbackModel": "qwen2.5-coder:3b",
    }):
        response = client.get(
            "/api/agent/status",
            base_url="https://app.sqxedgesuite.org",
            headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
    data = response.get_json()
    assert response.status_code == 200
    assert data["active"] is True
    assert data["access"]["remote"] is True
    assert data["access"]["capabilityMode"] == "tester_safe"
    assert data["access"]["monitorVisible"] is False
    assert data["inbox"]["enabled"] is False
    assert data["sqx142Compat"]["visible"] is False
    assert data["sqx142Performance"]["visible"] is False


def test_agent_remote_capabilities_exclude_local_inbox_and_write_actions():
    client = server.app.test_client()
    session_status = {
        "session": {"active": True, "email_ref": "te***@example.invalid", "entitlement_kind": "tester_free"},
        "entitlement": {"kind": "tester_free", "status": "active"},
        "access": {"allowed": True, "feature_scope": "full"},
    }
    with patch.object(server, "_remote_session_status_for_request", return_value=(session_status, "device-1")):
        response = client.get(
            "/api/agent/capabilities",
            base_url="https://app.sqxedgesuite.org",
            headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
    data = response.get_json()
    action_ids = {item["id"] for item in data["capabilities"]}
    assert response.status_code == 200
    assert "inspect_inbox" not in action_ids
    assert "sqx142_compat_help" not in action_ids
    assert "sqx142_performance_help" not in action_ids
    assert not any(item.startswith("mark_step:") for item in action_ids)
    assert "open_stage_tool:capa1-generate" in action_ids


def test_sqx142_compat_status_is_local_operator_only_and_path_safe():
    client = server.app.test_client()
    with patch.object(server, "build_sqx142_status", return_value={
        "version": "sqx142-compat-status-v1",
        "ok": False,
        "status": "needs_hardening",
        "java": {"active": {"label": "Oracle 25"}, "reference": {"label": "Zulu 22"}},
        "privacy": {"local_paths_returned": False},
    }):
        response = client.get("/api/sqx142/compat/status")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "needs_hardening"
    assert data["privacy"]["local_paths_returned"] is False
    assert "C:\\" not in json.dumps(data, ensure_ascii=False)

    blocked = client.get(
        "/api/sqx142/compat/status",
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked.status_code == 403
    assert blocked.get_json()["error"] == "local_operator_required"


def test_sqx142_performance_status_is_local_operator_only_and_path_safe():
    client = server.app.test_client()
    with patch.object(server, "build_sqx142_performance_status", return_value={
        "version": "sqx142-performance-status-v1",
        "ok": False,
        "status": "warn",
        "activeProfile": {"id": "baseline_143_safe"},
        "resources": {"disk": {"state": "warn", "freeHuman": "81.1 GB"}},
        "warnings": ["disk_free_below_recommended"],
        "privacy": {"local_paths_returned": False},
    }):
        response = client.get("/api/sqx142/performance/status")
    data = response.get_json()
    assert response.status_code == 200
    assert data["status"] == "warn"
    assert data["activeProfile"]["id"] == "baseline_143_safe"
    assert data["privacy"]["local_paths_returned"] is False
    assert "C:\\" not in json.dumps(data, ensure_ascii=False)

    blocked = client.get(
        "/api/sqx142/performance/status",
        base_url="https://app.sqxedgesuite.org",
        headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
        environ_base={"REMOTE_ADDR": "127.0.0.1"},
    )
    assert blocked.status_code == 403
    assert blocked.get_json()["error"] == "local_operator_required"


def test_agent_plan_and_execute_returns_validated_ui_command():
    client = server.app.test_client()
    with patch.object(server.OllamaClient, "status", return_value={"available": False, "model": "qwen3.5:latest"}):
        planned = client.post(
            "/api/agent/plan",
            json={
                "message": "abre project generator",
                "edgeFactoryState": {"version": "edge-factory-state-v1", "activeStep": "capa1-generate"},
            },
        )
    plan = planned.get_json()
    assert planned.status_code == 200
    assert plan["ok"] is True
    assert plan["recommendedAction"]["id"] == "open_stage_tool:capa1-generate"
    assert plan["requiresConfirmation"] is True

    confirmation = client.post("/api/agent/confirm", json={
        "actionId": plan["recommendedAction"]["id"],
        "arguments": plan["recommendedAction"]["arguments"],
    }).get_json()
    executed = client.post("/api/agent/execute", json={
        "actionId": plan["recommendedAction"]["id"],
        "confirmationToken": confirmation["confirmation"]["token"],
        "arguments": plan["recommendedAction"]["arguments"],
    })
    result = executed.get_json()
    assert executed.status_code == 200
    assert result["ok"] is True
    assert result["uiCommand"]["type"] == "open_tool"
    assert result["uiCommand"]["tool"] == "projectgen"


def test_agent_capabilities_question_uses_fixed_answer_without_ollama():
    client = server.app.test_client()
    with patch.object(server.OllamaClient, "status", return_value={"available": False, "model": "qwen3.5:latest"}):
        response = client.post("/api/agent/plan", json={"message": "que eres capaz de hacer?"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is True
    assert data["source"] == "fixed_capabilities"
    assert data["recommendedAction"]["id"] == "capabilities_help"
    assert data["requiresConfirmation"] is False
    assert "emails, grants, checkout, Cloudflare" in data["reply"]


def test_agent_sqx142_compat_question_uses_fixed_local_answer():
    client = server.app.test_client()
    with patch.object(server, "build_sqx142_status", return_value={
        "version": "sqx142-compat-status-v1",
        "ok": False,
        "status": "needs_hardening",
        "java": {"active": {"label": "Oracle 25"}, "reference": {"label": "Zulu 22"}},
        "blockers": ["java_runtime_mismatch"],
        "recommendation": "Alinear runtime.",
        "privacy": {"local_paths_returned": False},
    }):
        response = client.post("/api/agent/plan", json={"message": "estado compatibilidad SQX 142 build 143"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["source"] == "fixed_sqx142_compat"
    assert data["recommendedAction"]["id"] == "sqx142_compat_help"
    assert "Oracle 25" in data["reply"]
    assert "Zulu 22" in data["reply"]


def test_agent_sqx142_performance_question_uses_fixed_local_answer():
    client = server.app.test_client()
    with patch.object(server, "build_sqx142_performance_status", return_value={
        "version": "sqx142-performance-status-v1",
        "ok": False,
        "status": "warn",
        "activeProfile": {"id": "baseline_143_safe"},
        "resources": {"disk": {"state": "warn", "freeHuman": "81.1 GB"}},
        "compatibility": {"runtime": "Zulu 22.32+15", "status": "ok"},
        "intelligence": {
            "views": {"presentCount": 6, "expectedCount": 6, "missingCount": 0, "ok": True},
            "latestEvidence": {"filename": "performance_next_action_20260523_091502.json"},
            "recommendation": {"id": "ready_for_perf1_closeout", "label": "PERF1 esta listo para cierre operativo"},
            "liveGuard": {"state": "clean_idle", "alertCount": 0},
        },
        "warnings": ["disk_free_below_recommended"],
        "privacy": {"local_paths_returned": False},
    }):
        response = client.post("/api/agent/plan", json={"message": "analiza rendimiento SQX 142 y perfil jvm"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["source"] == "fixed_sqx142_performance"
    assert data["recommendedAction"]["id"] == "sqx142_performance_help"
    assert "baseline_143_safe" in data["reply"]
    assert "81.1 GB" in data["reply"]
    assert "6/6 views OK" in data["reply"]
    assert "PERF1 esta listo para cierre operativo" in data["reply"]
    assert "Live Guard: clean_idle" in data["reply"]


def test_agent_capabilities_question_uses_remote_safe_answer_for_testers():
    client = server.app.test_client()
    session_status = {
        "session": {"active": True, "email_ref": "te***@example.invalid", "entitlement_kind": "tester_free"},
        "entitlement": {"kind": "tester_free", "status": "active"},
        "access": {"allowed": True, "feature_scope": "full"},
    }
    with patch.object(server, "_remote_session_status_for_request", return_value=(session_status, "device-1")):
        response = client.post(
            "/api/agent/plan",
            json={"message": "que eres capaz de hacer?"},
            base_url="https://app.sqxedgesuite.org",
            headers={"Cf-Access-Authenticated-User-Email": "tester@example.invalid"},
            environ_base={"REMOTE_ADDR": "127.0.0.1"},
        )
    data = response.get_json()
    assert response.status_code == 200
    assert data["source"] == "fixed_capabilities"
    assert "modo tester seguro" in data["reply"]
    assert "monitor local del servidor" in data["reply"]
    assert "bandeja local del creador" in data["reply"]


def test_remote_operator_start_connects_ollama_before_ready_state():
    script = (server.PROJECT_ROOT / "tools" / "remote_operator_start.ps1").read_text(encoding="utf-8")
    assert "http://127.0.0.1:5050/api/agent/status" in script
    assert "$ollamaStatus = Get-OllamaStatus $agentStatusUrl" in script
    assert "$backendHealth.ok -and $null -ne $tunnelProcess -and $ollamaStatus.ok" in script


def test_remote_operator_monitor_tracks_sqx142_compatibility_status():
    status_script = (server.PROJECT_ROOT / "tools" / "remote_operator_status.ps1").read_text(encoding="utf-8")
    hta = (server.PROJECT_ROOT / "tools" / "remote_operator_monitor.hta").read_text(encoding="utf-8")
    probe = (server.PROJECT_ROOT / "tools" / "remote_operator_probe.ps1").read_text(encoding="utf-8")
    combined = "\n".join([status_script, hta, probe])
    assert "/api/sqx142/compat/status" in combined
    assert "Comprobando SQX 142" in combined
    assert "SQX 142:" in combined


def test_remote_operator_monitor_tracks_sqx142_performance_status():
    status_script = (server.PROJECT_ROOT / "tools" / "remote_operator_status.ps1").read_text(encoding="utf-8")
    hta = (server.PROJECT_ROOT / "tools" / "remote_operator_monitor.hta").read_text(encoding="utf-8")
    probe = (server.PROJECT_ROOT / "tools" / "remote_operator_probe.ps1").read_text(encoding="utf-8")
    combined = "\n".join([status_script, hta, probe])
    assert "/api/sqx142/performance/status" in combined
    assert "Comprobando rendimiento SQX 142" in combined
    assert "SQX142 Performance:" in combined
    assert "intelligence" in combined
    assert "recommendation" in combined
    assert "latestEvidence" in combined
    assert "liveGuard" in combined
    assert "views " in combined


def test_agent_translate_source_code_uses_local_ollama_only():
    client = server.app.test_client()
    with patch.object(server.OllamaClient, "status", return_value={"available": True, "model": "qwen3.5:latest"}), patch.object(
        server.OllamaClient,
        "chat_text",
        return_value="```mql5\n// translated\n```",
    ) as chat_text:
        response = client.post(
            "/api/agent/translate-source-code",
            json={"sourceCode": "if LongEntry then Buy;", "target": "MQL5 (MetaTrader 5)"},
        )
    data = response.get_json()
    assert response.status_code == 200
    assert data["ok"] is True
    assert data["code"] == "// translated"
    assert data["privacy"]["provider"] == "ollama_local"
    assert data["privacy"]["external_api_called"] is False
    chat_text.assert_called_once()
    assert chat_text.call_args.kwargs["model"] == "qwen2.5-coder:1.5b"
    assert chat_text.call_args.kwargs["num_predict"] == 900


def test_agent_translate_source_code_strips_trailing_markdown_and_explanation():
    assert server._strip_code_fences("// translated\n```\n\nExplanation") == "// translated"


def test_sqx142_source_translator_patch_removes_external_openai_calls():
    html = """
<title>Source Code Translator</title>
<h1>🔄 Source Code Translator</h1>
<label for="apiKey">OpenAI API Key</label>
<input type="password" id="apiKey" placeholder="sk-proj-..." autocomplete="off">
<option value="gpt-5.4" selected>GPT-5.4</option>
<button class="btn btn-secondary" id="btnFetchModels" title="Fetch latest models from OpenAI API">⟳ Refresh Models</button>
<script>
function doTranslate(){
  fetch('https://api.openai.com/v1/chat/completions', {});
}

// ── Fetch models from OpenAI API
$('btnFetchModels').addEventListener('click', function(){
  fetch('https://api.openai.com/v1/models', {});
});

// ── PostMessage listener
function doFixCode(){
  fetch('https://api.openai.com/v1/responses', {});
}

// ── Init
</script>
"""
    patched = patch_html(html)
    assert "api.openai.com" not in patched
    assert "OpenAI API Key" not in patched
    assert "sk-proj" not in patched
    assert "http://127.0.0.1:5050/api/agent/translate-source-code" in patched
    assert "qwen3.5:latest" in patched
