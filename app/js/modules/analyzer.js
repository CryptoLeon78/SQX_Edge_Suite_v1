(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  const ASSET_PRESETS = {
    FOREX: {
      min_pf: 1.4, min_win: 55, max_dd: 15, min_retdd: 4.0, min_sqn: 2.0, min_rexp: 0.15,
      regex: /EUR|GBP|USD|JPY|AUD|CAD|CHF|NZD/i
    },
    INDICES: {
      min_pf: 1.5, min_win: 52, max_dd: 20, min_retdd: 5.0, min_sqn: 2.5, min_rexp: 0.20,
      regex: /USA|NAS|NDX|DAX|GER|US30|DOW|SP500/i
    },
    CRYPTO: {
      min_pf: 1.8, min_win: 45, max_dd: 30, min_retdd: 6.0, min_sqn: 3.0, min_rexp: 0.30,
      regex: /BTC|ETH|SOL|BNB|XRP/i
    },
    GENERIC: { min_pf: 1.4, min_win: 50, max_dd: 20, min_retdd: 4.0, min_sqn: 2.0, min_rexp: 0.15 }
  };

  let analyzerState = {
    strategies: [],
    currentPreset: 'GENERIC',
    currentStrategyId: null
  };

  function init() {
    const fileInput = document.getElementById('analyzer-file-input');
    if (fileInput) {
      fileInput.addEventListener('change', handleFileSelect);
    }

    const topProxy = document.getElementById('analyzer-top-scroll');
    const resultsContainer = document.getElementById('analyzer-results');

    if (topProxy && resultsContainer) {
      topProxy.addEventListener('scroll', () => {
        const wrap = resultsContainer.querySelector('.analyzer-table-wrap');
        if (wrap) wrap.scrollLeft = topProxy.scrollLeft;
      });
    }

    // Modal bindings
    const closeBtn = document.querySelector('#analyzer-modal .close-btn');
    if (closeBtn) closeBtn.onclick = closeC2Modal;

    const cancelBtn = document.querySelector('#analyzer-modal .export-btn.secondary');
    if (cancelBtn) cancelBtn.onclick = closeC2Modal;

    const confirmBtn = document.querySelector('#analyzer-modal .export-btn.primary');
    if (confirmBtn) confirmBtn.onclick = confirmC2Export;

    const bloqueSelect = document.getElementById('c2-bloque-select');
    if (bloqueSelect) {
      bloqueSelect.onchange = (e) => toggleBloqueOtro(e.target.value);
    }

    const resetBtn = document.getElementById('analyzer-reset-btn');
    if (resetBtn) resetBtn.onclick = reset;
  }

  async function handleFileSelect(e) {
    const file = e.target.files[0];
    if (!file) return;

    const text = await file.text();
    const rows = parseCSV(text);

    analyzerState.strategies = rows.map((r, idx) => {
      const rawName = r['Strategy Name'] || '';
      let stratNum = rawName.replace(/Strategy\s+/i, '').trim();
      if (!stratNum) stratNum = `ID-${idx}`;

      return {
        ...r,
        _id: stratNum,
        _rawName: rawName,
        passed: checkStrategy(r)
      };
    });

    render();
  }

  function parseCSV(text) {
    const lines = text.split(/\r?\n/).filter(l => l.trim());
    if (lines.length < 2) return [];

    const firstLine = lines[0];
    const sep = firstLine.includes(';') ? ';' : ',';

    const headers = firstLine.split(sep).map(h => h.trim().replace(/"/g, ''));
    return lines.slice(1).map(line => {
      const values = line.split(sep).map(v => v.trim().replace(/"/g, ''));
      const obj = {};
      headers.forEach((h, i) => obj[h] = values[i]);
      return obj;
    });
  }

  function checkStrategy(s) {
    const p = ASSET_PRESETS[analyzerState.currentPreset];
    const metrics = {
      pf: parseFloat(s['Profit Factor']) || 0,
      win: parseFloat(s['Win %']) || 0,
      dd: parseFloat(s['Max DD %']) || 0,
      retdd: parseFloat(s['Ret/DD Ratio']) || 0,
      sqn: parseFloat(s['SQN']) || 0,
      rexp: parseFloat(s['R Expectancy']) || 0
    };

    return metrics.pf >= p.min_pf &&
           metrics.win >= p.min_win &&
           metrics.dd <= p.max_dd &&
           metrics.retdd >= p.min_retdd &&
           metrics.sqn >= p.min_sqn &&
           metrics.rexp >= p.min_rexp;
  }

  function render() {
    const container = document.getElementById('analyzer-results');
    if (!container) return;

    if (analyzerState.strategies.length === 0) {
      container.innerHTML = '<div class="ps-na-text" style="text-align:center; padding:40px;">Sube un DatabankExport.csv para comenzar el análisis...</div>';
      return;
    }

    const html = `
      <div class="analyzer-table-wrap">
        <table class="analyzer-table">
          <thead>
            <tr>
              <th>Status</th>
              <th>Strategy Name</th>
              <th>PF</th>
              <th>Win%</th>
              <th>Max DD%</th>
              <th>Ret/DD</th>
              <th>SQN</th>
              <th>R Exp</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            ${analyzerState.strategies.map(s => renderRow(s)).join('')}
          </tbody>
        </table>
      </div>
    `;

    container.innerHTML = html;

    const wrap = container.querySelector('.analyzer-table-wrap');
    const topProxy = document.getElementById('analyzer-top-scroll');
    if (wrap && topProxy) {
      wrap.addEventListener('scroll', () => {
        topProxy.scrollLeft = wrap.scrollLeft;
      });
    }

    setTimeout(() => {
      const table = container.querySelector('.analyzer-table');
      const proxyInner = topProxy ? topProxy.querySelector('div') : null;
      if (table && proxyInner) {
        proxyInner.style.width = table.offsetWidth + 'px';
        topProxy.style.display = table.offsetWidth > wrap.offsetWidth ? 'block' : 'none';
      }
    }, 100);
  }

  function renderRow(s) {
    const isPassed = s.passed;
    return `
      <tr>
        <td><span class="metric-badge ${isPassed ? 'badge-passed' : 'badge-failed'}">${isPassed ? 'PASSED' : 'REJECTED'}</span></td>
        <td style="font-weight:700">${s._rawName}</td>
        <td>${s['Profit Factor']}</td>
        <td>${s['Win %']}%</td>
        <td>${s['Max DD %']}%</td>
        <td>${s['Ret/DD Ratio']}</td>
        <td>${s['SQN']}</td>
        <td>${s['R Expectancy']}</td>
        <td>
          <button class="export-btn" data-c2-id="${s._id}" ${!isPassed ? 'style="opacity:0.5; cursor:not-allowed;"' : ''}>⚡ C2</button>
        </td>
      </tr>
    `;
  }

  // Event delegation for C2 buttons
  document.addEventListener('click', (e) => {
    if (e.target.matches('[data-c2-id]')) {
      const id = e.target.getAttribute('data-c2-id');
      openC2Modal(id);
    }
  });

  function openC2Modal(id) {
    const s = analyzerState.strategies.find(x => x._id === id);
    if (!s || !s.passed) return;

    analyzerState.currentStrategyId = id;
    const modal = document.getElementById('analyzer-modal');
    if (modal) {
      modal.style.display = 'flex';
      document.getElementById('c2-activo').value = '';
      document.getElementById('c2-direccion').value = 'LONG';
      document.getElementById('c2-tf').value = '';
      document.getElementById('c2-indicador').value = '';
      document.getElementById('c2-bloque-select').value = 'TENDENCIA';
      document.getElementById('c2-bloque-manual').style.display = 'none';
      document.getElementById('c2-bloque-manual').value = '';
    }
  }

  function closeC2Modal() {
    const modal = document.getElementById('analyzer-modal');
    if (modal) modal.style.display = 'none';
  }

  function toggleBloqueOtro(val) {
    const manualInput = document.getElementById('c2-bloque-manual');
    if (manualInput) {
      manualInput.style.display = val === 'OTROS' ? 'block' : 'none';
    }
  }

  function confirmC2Export() {
    const id = analyzerState.currentStrategyId;
    const s = analyzerState.strategies.find(x => x._id === id);
    if (!s) return;

    const activo = document.getElementById('c2-activo').value.trim().toUpperCase() || 'ASSET';
    const direccion = document.getElementById('c2-direccion').value;
    const tf = document.getElementById('c2-tf').value.trim().toUpperCase() || 'TF';
    const indicador = document.getElementById('c2-indicador').value.trim().toUpperCase() || 'IND';

    const bloqueSelect = document.getElementById('c2-bloque-select').value;
    const bloqueManual = document.getElementById('c2-bloque-manual').value.trim().toUpperCase();
    const bloque = bloqueSelect === 'OTROS' ? (bloqueManual || 'OTROS') : bloqueSelect;

    const fileName = `template_${activo}_${direccion}_${tf}_${indicador}_${bloque}_${id}.cfx`;

    console.log(`[C2 Export] Generando: ${fileName}`);
    alert(`Estrategia Certificada:\n${fileName}\n\nExportación preparada para Edge Pipeline.`);

    closeC2Modal();
  }

  function reset() {
    if (analyzerState.strategies.length > 0 && !confirm('¿Resetear análisis actual?')) return;

    analyzerState.strategies = [];
    analyzerState.currentStrategyId = null;

    const fileInput = document.getElementById('analyzer-file-input');
    if (fileInput) fileInput.value = '';

    render();
  }

  var api = { init, render, reset, openC2Modal, confirmC2Export };

  // Register with institutional dashboard
  if (SQX.registerModule) {
    SQX.registerModule('modules/analyzer', api);
    SQX.registerModule('analyzer', api);
  }

  // Backward compatibility for manual calls if needed
  SQX.analyzer = api;
  SQX.Analyzer = api;

})(window);
