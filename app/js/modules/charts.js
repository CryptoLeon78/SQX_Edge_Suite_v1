(function(global) {
  'use strict';

  var SQX = global.SQX = global.SQX || {};

  function renderHistoryChart(assetId, data, macroEvents, chartCfg) {
    if (!data) return '<div class="history-no-data">Sin histórico disponible para ' + assetId + ' (no estaba en Darwinex).</div>';

    var cfg = chartCfg || {};
    var W = cfg.width || 720;
    var H = cfg.height || 220;
    var padL = cfg.padL || 44;
    var padR = cfg.padR || 14;
    var padT = cfg.padT || 18;
    var padB = cfg.padB || 32;
    var innerW = W - padL - padR;
    var innerH = H - padT - padB;
    var v = data.v;
    var n = v.length;
    var startParts = data.start.split('-').map(Number);
    var sy = startParts[0];
    var sm = startParts[1];

    function xAt(i) {
      return padL + (n > 1 ? (i / (n - 1)) * innerW : innerW / 2);
    }

    var minV = Math.min.apply(null, v);
    var maxV = Math.max.apply(null, v);
    var useLog = (maxV / Math.max(minV, 0.001)) > 3;
    var tx = useLog ? Math.log : function(x) { return x; };
    var minT = tx(minV);
    var maxT = tx(maxV);
    var rangeT = (maxT - minT) || 1;

    function yAt(val) {
      return padT + (1 - (tx(val) - minT) / rangeT) * innerH;
    }

    var SMA_PERIOD = cfg.smaPeriod || 24;
    var sma = v.map(function(_value, i) {
      if (i < SMA_PERIOD - 1) return null;
      var sum = 0;
      for (var k = i - (SMA_PERIOD - 1); k <= i; k += 1) sum += v[k];
      return sum / SMA_PERIOD;
    });

    var regimeRaw = v.map(function(_value, i) {
      return sma[i] === null ? null : (v[i] > sma[i] ? 1 : -1);
    });

    var MIN_BAND_MONTHS = cfg.minBandMonths || 6;
    var bands = [];
    var curStart = -1;
    var curBull = null;
    for (var i = 0; i < n; i += 1) {
      if (regimeRaw[i] === null) continue;
      var isBull = regimeRaw[i] === 1;
      if (curBull === null) {
        curBull = isBull;
        curStart = i;
        continue;
      }
      if (isBull !== curBull) {
        var sustained = true;
        for (var lookAhead = i; lookAhead < Math.min(i + MIN_BAND_MONTHS, n); lookAhead += 1) {
          if (regimeRaw[lookAhead] !== null && (regimeRaw[lookAhead] === 1) !== isBull) {
            sustained = false;
            break;
          }
        }
        if (sustained) {
          bands.push({ start: curStart, end: i - 1, bull: curBull });
          curStart = i;
          curBull = isBull;
        }
      }
    }
    if (curStart !== -1) bands.push({ start: curStart, end: n - 1, bull: curBull });

    var path = '';
    var smaPath = '';
    var smaStarted = false;
    for (var pi = 0; pi < n; pi += 1) {
      path += (pi === 0 ? 'M' : 'L') + xAt(pi).toFixed(1) + ',' + yAt(v[pi]).toFixed(1) + ' ';
      if (sma[pi] !== null) {
        smaPath += (smaStarted ? 'L' : 'M') + xAt(pi).toFixed(1) + ',' + yAt(sma[pi]).toFixed(1) + ' ';
        smaStarted = true;
      }
    }

    var totalMonths = n + (sm - 1);
    var ey = sy + Math.floor((totalMonths - 1) / 12);
    var span = ey - sy;
    var tickEvery = span >= 16 ? 3 : span >= 10 ? 2 : 1;
    var yearTicks = [];
    for (var yy = Math.ceil(sy / tickEvery) * tickEvery; yy <= ey; yy += tickEvery) {
      var idx = (yy - sy) * 12 - (sm - 1);
      if (idx >= 0 && idx < n) yearTicks.push({ year: yy, idx: idx });
    }

    var svg = '<svg class="history-chart" viewBox="0 0 ' + W + ' ' + H + '" preserveAspectRatio="xMidYMid meet">';
    svg += '<rect x="0" y="0" width="' + W + '" height="' + H + '" fill="#11141d" rx="6"/>';

    bands.forEach(function(band) {
      var x1 = xAt(band.start);
      var x2 = xAt(band.end);
      var fill = band.bull ? 'rgba(34,197,94,0.18)' : 'rgba(239,68,68,0.18)';
      svg += '<rect x="' + x1.toFixed(1) + '" y="' + padT + '" width="' + (x2 - x1).toFixed(1) + '" height="' + innerH + '" fill="' + fill + '"/>';
    });

    var gridVals = [];
    if (useLog) {
      [50, 75, 100, 150, 200, 300, 500, 750, 1000, 1500, 2000, 3000, 5000].forEach(function(decade) {
        if (decade >= minV * 0.9 && decade <= maxV * 1.1) gridVals.push(decade);
      });
    } else {
      var span2 = maxV - minV;
      var step = span2 < 30 ? 5 : span2 < 80 ? 10 : 20;
      for (var g = Math.floor(minV / step) * step; g <= maxV; g += step) {
        if (g >= minV * 0.95) gridVals.push(g);
      }
    }

    gridVals.forEach(function(g) {
      var yp = yAt(g);
      svg += '<line x1="' + padL + '" y1="' + yp.toFixed(1) + '" x2="' + (W - padR) + '" y2="' + yp.toFixed(1) + '" stroke="#2e3348" stroke-width="0.5" stroke-dasharray="2,3"/>';
      svg += '<text x="' + (padL - 6) + '" y="' + (yp + 3).toFixed(1) + '" text-anchor="end" font-size="10" fill="#9ca3af">' + g.toFixed(0) + '</text>';
    });

    if (100 >= minV && 100 <= maxV) {
      var y100 = yAt(100);
      svg += '<line x1="' + padL + '" y1="' + y100.toFixed(1) + '" x2="' + (W - padR) + '" y2="' + y100.toFixed(1) + '" stroke="#3b82f6" stroke-width="0.7" stroke-dasharray="3,2" opacity="0.4"/>';
    }

    yearTicks.forEach(function(tick) {
      var xp = xAt(tick.idx);
      svg += '<line x1="' + xp.toFixed(1) + '" y1="' + padT + '" x2="' + xp.toFixed(1) + '" y2="' + (H - padB + 2) + '" stroke="#2e3348" stroke-width="0.5"/>';
      svg += '<text x="' + xp.toFixed(1) + '" y="' + (H - padB + 15) + '" text-anchor="middle" font-size="10" fill="#9ca3af">' + tick.year + '</text>';
    });

    (macroEvents || []).forEach(function(ev) {
      var parts = ev.date.split('-').map(Number);
      var eventIdx = (parts[0] - sy) * 12 + (parts[1] - sm);
      if (eventIdx < 0 || eventIdx >= n) return;
      var xp = xAt(eventIdx);
      svg += '<line x1="' + xp.toFixed(1) + '" y1="' + padT + '" x2="' + xp.toFixed(1) + '" y2="' + (H - padB) + '" stroke="' + ev.color + '" stroke-width="1.2" stroke-dasharray="3,2" opacity="0.7"><title>' + ev.label + ' (' + ev.date + ')</title></line>';
      svg += '<circle cx="' + xp.toFixed(1) + '" cy="' + (padT - 2) + '" r="3.2" fill="' + ev.color + '"><title>' + ev.label + ' (' + ev.date + ')</title></circle>';
    });

    svg += '<path d="' + smaPath + '" fill="none" stroke="#9ca3af" stroke-width="1" stroke-dasharray="3,2" opacity="0.55"/>';
    svg += '<path d="' + path + '" fill="none" stroke="#3b82f6" stroke-width="1.7"/>';

    var last = v[n - 1];
    var first = v[0];
    var totalChange = ((last / first - 1) * 100);
    var tcStr = (totalChange >= 0 ? '+' : '') + totalChange.toFixed(1) + '%';
    var tcColor = totalChange >= 0 ? '#22c55e' : '#ef4444';
    svg += '<text x="' + (W - padR) + '" y="' + (padT - 4) + '" text-anchor="end" font-size="11" fill="' + tcColor + '" font-weight="700">' + tcStr + ' (' + data.start + ' → hoy)</text>';

    svg += '</svg>';
    return svg;
  }

  SQX.charts = SQX.charts || {
    renderHistoryChart: renderHistoryChart
  };

  if (SQX.registerModule) {
    SQX.registerModule('charts', SQX.charts);
  }
})(window);
