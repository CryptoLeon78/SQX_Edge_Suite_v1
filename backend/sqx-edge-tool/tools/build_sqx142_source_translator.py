from __future__ import annotations

import argparse
import json
import re
import zipfile
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOURCE = REPO_ROOT / "material de diagnostico" / "material_a_implementar" / "SQExtension-SourceCode-Translator.sxp"
DEFAULT_OUTPUT = REPO_ROOT / ".local" / "sqx_extensions" / "SQExtension-SourceCode-Translator-Ollama-SQX142.sxp"
PLUGIN_HTML = "extend/ResultsPlugins/Source Code Translator/index.html"


LOCAL_TRANSLATE_FUNCTION = r"""function doTranslate(){
  var src = sourceCode.value.trim();
  if(!src){ setStatus('Please paste or fetch source code first.','error'); sourceCode.focus(); return; }

  var target = targetLang.value;
  $('outputLabel').textContent = '📄 ' + target.split('(')[0].trim();
  setStatus('<span class="spinner"></span>Translating locally with Ollama…');
  $('btnTranslate').disabled = true;
  outputCode.value = '';
  $('outputInfo').textContent = '';

  fetch('http://127.0.0.1:5050/api/agent/translate-source-code', {
    method:'POST',
    headers:{ 'Content-Type':'application/json' },
    body: JSON.stringify({ mode:'translate', sourceCode: src, target: target })
  }).then(function(resp){
    return resp.json().then(function(data){ return { ok: resp.ok, data: data }; });
  }).then(function(result){
    $('btnTranslate').disabled = false;
    if(!result.ok || !result.data.ok){
      var msg = (result.data && (result.data.error || result.data.message)) || 'local_backend_error';
      throw new Error(msg);
    }
    outputCode.value = stripCodeFences(result.data.code || '');
    outputCode.scrollTop = outputCode.scrollHeight;
    $('outputInfo').textContent = outputCode.value.length.toLocaleString()+' chars · '+(result.data.model || 'Ollama local');
    setStatus('✔ Local translation complete.','success');
  }).catch(function(err){
    $('btnTranslate').disabled = false;
    setStatus('Local Ollama error: '+err.message,'error');
    console.error('Local translation error:', err);
  });
}
"""


LOCAL_FETCH_MODELS_HANDLER = r"""$('btnFetchModels').addEventListener('click', function(){
  setStatus('<span class="spinner"></span>Checking local Ollama…');
  fetch('http://127.0.0.1:5050/api/agent/status')
    .then(function(r){ return r.json(); })
    .then(function(data){
      var provider = data.provider || {};
      modelSelect.innerHTML = '';
      var opt = document.createElement('option');
      opt.value = provider.model || provider.configuredModel || 'ollama-local';
      opt.textContent = opt.value + ' (local)';
      modelSelect.appendChild(opt);
      keyStatus.textContent = provider.available ? '✔ Ollama local active' : 'Ollama unavailable';
      keyStatus.className = 'key-status ' + (provider.available ? 'saved' : 'missing');
      setStatus(provider.available ? '✔ Local model ready.' : 'Ollama is not available. Start SQX Edge server first.', provider.available ? 'success' : 'error');
    })
    .catch(function(err){ setStatus('Local backend unavailable: '+err.message,'error'); });
});
"""


LOCAL_FIX_FUNCTION = r"""function doFixCode(){
  var code = outputCode.value.trim();
  if(!code){ setFixStatus('No translated code to fix. Translate first.','error'); return; }
  var feedback = feedbackText.value.trim();
  if(!feedback && screenshots.length === 0){
    setFixStatus('Describe the compiler/runtime error. Local Ollama v1 ignores screenshots.','error');
    return;
  }

  var target = targetLang.value;
  setFixStatus('<span class="spinner"></span>Fixing locally with Ollama…');
  $('btnFixCode').disabled = true;
  outputCode.value = '';
  $('outputInfo').textContent = '';
  screenshots = [];
  renderThumbnails();
  updateScreenshotCount();

  fetch('http://127.0.0.1:5050/api/agent/translate-source-code', {
    method:'POST',
    headers:{ 'Content-Type':'application/json' },
    body: JSON.stringify({ mode:'fix', sourceCode: code, target: target, feedback: feedback })
  }).then(function(resp){
    return resp.json().then(function(data){ return { ok: resp.ok, data: data }; });
  }).then(function(result){
    $('btnFixCode').disabled = false;
    if(!result.ok || !result.data.ok){
      var msg = (result.data && (result.data.error || result.data.message)) || 'local_backend_error';
      throw new Error(msg);
    }
    outputCode.value = stripCodeFences(result.data.code || '');
    $('outputInfo').textContent = outputCode.value.length.toLocaleString()+' chars · '+(result.data.model || 'Ollama local');
    setFixStatus('✔ Local fix complete.','success');
  }).catch(function(err){
    $('btnFixCode').disabled = false;
    setFixStatus('Local Ollama error: '+err.message,'error');
    console.error('Local fix error:', err);
  });
}
"""


def _replace_between(text: str, pattern: str, replacement: str) -> str:
    new_text, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"Expected exactly one replacement for pattern: {pattern[:80]}")
    return new_text


def patch_html(html: str) -> str:
    html = html.replace("<title>Source Code Translator</title>", "<title>Local Source Code Translator</title>")
    html = html.replace("<h1>🔄 Source Code Translator</h1>", "<h1>🔄 Source Code Translator · Local Ollama</h1>")
    html = html.replace('<label for="apiKey">OpenAI API Key</label>', '<label for="apiKey">Local backend</label>')
    html = html.replace('<input type="password" id="apiKey" placeholder="sk-proj-..." autocomplete="off">', '<input type="text" id="apiKey" value="http://127.0.0.1:5050" readonly autocomplete="off">')
    html = html.replace('<option value="gpt-5.4" selected>GPT-5.4</option>', '<option value="qwen3.5:latest" selected>qwen3.5:latest local</option>')
    html = re.sub(r"\s*<option value=\"gpt-[^\"]+\">[^<]+</option>", "", html)
    html = re.sub(r"\s*<option value=\"o[^\"]+\">[^<]+</option>", "", html)
    html = html.replace('title="Fetch latest models from OpenAI API">⟳ Refresh Models', 'title="Check local Ollama model">⟳ Check Ollama')
    html = html.replace("var STORAGE_KEY = 'sqx_translator_api_key';", "var STORAGE_KEY = 'sqx_translator_local_backend';")
    html = html.replace("if(saved){ keyStatus.textContent='✔ Key saved'; keyStatus.className='key-status saved'; }", "if(saved){ keyStatus.textContent='✔ Local backend set'; keyStatus.className='key-status saved'; }")
    html = html.replace("else { keyStatus.textContent='No key saved'; keyStatus.className='key-status missing'; }", "else { keyStatus.textContent='Backend local pending'; keyStatus.className='key-status missing'; }")
    html = _replace_between(
        html,
        r"function doTranslate\(\)\{.*?\n\}\n\n// ── Fetch models from OpenAI API",
        LOCAL_TRANSLATE_FUNCTION + "\n// ── Fetch models from local SQX Edge server",
    )
    html = _replace_between(
        html,
        r"\$\(\'btnFetchModels\'\)\.addEventListener\('click', function\(\)\{.*?\n\}\);\n\n// ── PostMessage listener",
        LOCAL_FETCH_MODELS_HANDLER + "\n// ── PostMessage listener",
    )
    html = _replace_between(
        html,
        r"function doFixCode\(\)\{.*?\n\}\n\n// ── Init",
        LOCAL_FIX_FUNCTION + "\n// ── Init",
    )
    return html


def build_package(source: Path, output: Path) -> dict:
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source, "r") as zin, zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        names = zin.namelist()
        if PLUGIN_HTML not in names:
            raise RuntimeError(f"{PLUGIN_HTML} not found in {source}")
        for name in names:
            payload = zin.read(name)
            if name == PLUGIN_HTML:
                payload = patch_html(payload.decode("utf-8", errors="replace")).encode("utf-8")
            zout.writestr(name, payload)
    return {
        "ok": True,
        "source": str(source),
        "output": str(output),
        "pluginHtml": PLUGIN_HTML,
        "builtAt": datetime.now(timezone.utc).isoformat(),
        "externalApiRemoved": True,
        "localEndpoint": "http://127.0.0.1:5050/api/agent/translate-source-code",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SQX 142 local Ollama Source Code Translator .sxp")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = build_package(args.source, args.output)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print(f"Built: {result['output']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
