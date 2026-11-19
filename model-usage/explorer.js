/* No dependencies or network calls. All calculations use observed rows from the bundled snapshot. */
(function (root, factory) {
  'use strict';
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (root && root.document) {
    root.OpenRouterUsageExplorer = api;
    if (root.document.readyState === 'loading') root.document.addEventListener('DOMContentLoaded', function () { api.init(root.document, root.OPENROUTER_USAGE_DATA); });
    else api.init(root.document, root.OPENROUTER_USAGE_DATA);
  }
})(typeof window !== 'undefined' ? window : globalThis, function () {
  'use strict';
  const DEFAULT_MODEL_ID = 'tencent/hy4-flash-20261116';
  const ALL_COUNTRIES = 'all';
  const PAGE_SIZE = 25;
  const compareID = (a, b) => a < b ? -1 : a > b ? 1 : 0;
  function metricName(metric) {
    if (metric === 'tokens' || metric === 'total_tokens') return 'tokens';
    if (metric === 'requests') return 'requests';
    throw new RangeError('Measure must be tokens, total_tokens, or requests.');
  }
  function metricIndex(metric) { return metricName(metric) === 'tokens' ? 3 : 2; }
  function allCountries(country) { return country == null || country === ALL_COUNTRIES || country === 'ALL'; }
  function add(a, b) {
    if (!Number.isSafeInteger(b) || b < 0 || !Number.isSafeInteger(a + b)) throw new RangeError('An observed count is not a nonnegative safe integer.');
    return a + b;
  }
  function share(value, denominator) { return denominator > 0 ? value / denominator : null; }
  function countryLabel(data, code) {
    const entry = data.countries.find(c => c.code === code);
    if (entry && entry.name && entry.name !== code) return entry.name;
    if (code === 'suppressed') return 'Suppressed country group';
    if (code === 'unknown') return 'Unknown country';
    if (code === 'T1') return 'Tor network (T1)';
    try { return new Intl.DisplayNames(['en'], { type: 'region' }).of(code) || code; } catch (_) { return code; }
  }
  /** Returns observed model rows, a full-group denominator, and top-N coverage. Never expands missing cells. */
  function rankModels(data, country = ALL_COUNTRIES, metric = 'tokens', limit = 100) {
    const mi = metricIndex(metric), values = new Map();
    data.rows.forEach(row => {
      if (allCountries(country) || row[1] === country) values.set(row[0], add(values.get(row[0]) || 0, row[mi]));
    });
    let denominator = 0;
    const ranked = Array.from(values, ([index, value]) => {
      denominator = add(denominator, value);
      return { ...data.models[index], index, value };
    }).sort((a, b) => b.value - a.value || compareID(a.id, b.id));
    const cap = Number.isFinite(limit) ? Math.max(0, Math.floor(limit)) : ranked.length;
    const rows = ranked.slice(0, cap).map((row, index) => ({ ...row, rank: index + 1, share: share(row.value, denominator) }));
    const shownTotal = rows.reduce((sum, row) => add(sum, row.value), 0);
    return { rows, denominator, modelCount: ranked.length, shownCount: rows.length, shownTotal, topShare: share(shownTotal, denominator), country: allCountries(country) ? ALL_COUNTRIES : country, metric: metricName(metric) };
  }
  /** page is one-based. start/end are one-based item positions; both are zero for an empty list. */
  function paginate(items, page = 1, pageSize = PAGE_SIZE) {
    if (!Number.isSafeInteger(pageSize) || pageSize < 1) throw new RangeError('Page size must be a positive integer.');
    const pages = Math.max(1, Math.ceil(items.length / pageSize));
    const current = Math.min(pages, Math.max(1, Number.isFinite(page) ? Math.floor(page) : 1));
    const offset = (current - 1) * pageSize;
    return { items: items.slice(offset, offset + pageSize), page: current, pages, total: items.length, start: items.length ? offset + 1 : 0, end: Math.min(offset + pageSize, items.length) };
  }
  /** A real reported zero returns 0. A missing model-country observation returns null. */
  function observation(data, modelId, country = ALL_COUNTRIES, metric = 'tokens') {
    const index = data.models.findIndex(model => model.id === modelId), mi = metricIndex(metric);
    let total = null;
    data.rows.forEach(row => {
      if (row[0] === index && (allCountries(country) || row[1] === country)) total = add(total === null ? 0 : total, row[mi]);
    });
    return total;
  }
  /** All-country breakdown, regardless of the ranking's country selection. Zero denominator => null shares. */
  function countryBreakdown(data, modelId, metric = 'tokens') {
    const index = data.models.findIndex(model => model.id === modelId), mi = metricIndex(metric), values = new Map();
    data.rows.forEach(row => { if (row[0] === index) values.set(row[1], add(values.get(row[1]) || 0, row[mi])); });
    const total = values.size ? Array.from(values.values()).reduce(add, 0) : null;
    const rows = Array.from(values, ([code, value]) => ({ code, country: code, name: countryLabel(data, code), value, share: share(value, total), special: code === 'suppressed' || code === 'unknown' }))
      .sort((a, b) => b.value - a.value || compareID(a.code, b.code));
    return { rows, total, modelId, metric: metricName(metric) };
  }
  function buildCountryOptions(data) {
    const rows = data.countries.map(c => ({ code: c.code, name: countryLabel(data, c.code), special: c.code === 'suppressed' || c.code === 'unknown' }));
    rows.sort((a, b) => Number(a.special) - Number(b.special) || compareID(a.name, b.name));
    return [{ code: ALL_COUNTRIES, name: 'All country groups', special: false }, ...rows];
  }
  function recentTrend(data, metric = 'tokens') {
    const name = metricName(metric), field = name === 'tokens' ? 'total_tokens' : 'requests';
    const rows = (data.recentHy4 || []).slice().sort((a, b) => compareID(a.date, b.date)).map((row, i, array) => {
      const previous = i ? array[i - 1][field] : null;
      return { date: row.date, value: row[field], changeRatio: previous > 0 ? row[field] / previous - 1 : null };
    });
    return { rows, peak: rows.length ? Math.max(...rows.map(r => r.value)) : null, modelId: DEFAULT_MODEL_ID, metric: name };
  }
  function formatNumber(value) { return value == null ? 'Not separately reported' : new Intl.NumberFormat('en-US').format(value); }
  function formatCompact(value) {
    if (value == null) return 'Not separately reported';
    const units = [[1e12, 'T'], [1e9, 'B'], [1e6, 'M'], [1e3, 'K']];
    const unit = units.find(([size]) => value >= size);
    return unit ? new Intl.NumberFormat('en-US', { maximumFractionDigits: 2 }).format(value / unit[0]) + unit[1] : formatNumber(value);
  }
  function formatShare(value) {
    if (value == null) return 'N/A';
    if (value > 0 && value < 0.0001) return '<0.01%';
    return new Intl.NumberFormat('en-US', { style: 'percent', minimumFractionDigits: 0, maximumFractionDigits: 2 }).format(value);
  }
  function dateLabel(date, short = false) {
    return new Intl.DateTimeFormat('en-US', { month: short ? 'short' : 'long', day: 'numeric', ...(short ? {} : { year: 'numeric' }), timeZone: 'UTC' }).format(new Date(date + 'T00:00:00Z'));
  }
  function init(doc, data) {
    const status = doc.getElementById('app-status');
    if (!data || !Array.isArray(data.rows) || !Array.isArray(data.models) || !Array.isArray(data.countries)) {
      if (status) status.textContent = 'The local snapshot is unavailable. Please reload this page.';
      return;
    }
    const state = { country: ALL_COUNTRIES, metric: 'tokens', page: 1, modelId: data.models.some(m => m.id === DEFAULT_MODEL_ID) ? DEFAULT_MODEL_ID : data.models[0]?.id };
    const el = id => doc.getElementById(id);
    const node = (tag, className, text) => { const n = doc.createElement(tag); if (className) n.className = className; if (text !== undefined) n.textContent = text; return n; };
    const titleMetric = () => state.metric === 'tokens' ? 'Tokens' : 'Requests';
    const measure = () => state.metric === 'tokens' ? 'tokens' : 'requests';
    const groupName = () => allCountries(state.country) ? 'All country groups' : countryLabel(data, state.country);
    function bar(value, maximum) {
      const track = node('span', 'bar-track'); const fill = node('span', 'bar-fill');
      fill.style.width = (maximum > 0 ? Math.max(0, Math.min(100, value / maximum * 100)) : 0) + '%';
      track.append(fill); track.setAttribute('aria-hidden', 'true'); return track;
    }
    function setModel(id, fromRanking = false) {
      state.modelId = id; el('model-select').value = id;
      doc.querySelectorAll('.model-button').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.modelId === id)));
      renderBreakdown();
      if (fromRanking && doc.defaultView && doc.defaultView.matchMedia('(max-width: 800px)').matches) {
        el('breakdown-title').scrollIntoView({ block: 'start', behavior: 'auto' });
        el('breakdown-title').focus({ preventScroll: true });
      }
    }
    function renderRanking() {
      const ranking = rankModels(data, state.country, state.metric, 100), page = paginate(ranking.rows, state.page, PAGE_SIZE);
      state.page = page.page;
      el('ranking-title').textContent = ranking.shownCount < 100 ? 'Top ' + ranking.shownCount + ' reported models' : 'Top 100 models';
      el('ranking-unit').textContent = titleMetric(); el('value-column').textContent = titleMetric();
      el('ranking-context').textContent = groupName() + ' · ' + dateLabel(data.date_utc) + ' UTC · ' + formatNumber(ranking.modelCount) + ' observed model versions';
      el('ranking-denominator').textContent = formatNumber(ranking.denominator) + ' ' + measure() + ' across all ' + ranking.modelCount + ' disclosed models';
      el('ranking-coverage').textContent = 'Top ' + ranking.shownCount + ' account for ' + formatShare(ranking.topShare) + ' of this reported total.';
      doc.querySelectorAll('.page-description').forEach(n => { n.textContent = page.start + '–' + page.end + ' of ' + page.total + ' · Page ' + page.page + '/' + page.pages; });
      doc.querySelectorAll('.page-prev').forEach(n => { n.disabled = page.page <= 1; });
      doc.querySelectorAll('.page-next').forEach(n => { n.disabled = page.page >= page.pages; });
      const list = el('ranking-list'); list.replaceChildren(); list.start = page.start || 1;
      const maximum = ranking.rows[0]?.value || 0;
      page.items.forEach(row => {
        const li = node('li', 'ranking-row'), button = node('button', 'model-button'), line = node('span', 'model-line');
        button.type = 'button'; button.dataset.modelId = row.id; button.setAttribute('aria-pressed', String(row.id === state.modelId));
        button.setAttribute('aria-label', 'Rank ' + row.rank + ': ' + row.name + ', ' + row.id + ', ' + formatNumber(row.value) + ' ' + measure() + ', ' + formatShare(row.share) + ' of this group. Show global country breakdown.');
        button.title = row.id + '\n' + formatNumber(row.value) + ' ' + measure();
        line.append(node('span', 'rank-number', String(row.rank)));
        const label = node('span', 'model-label'); label.append(node('span', 'model-name', row.name), node('span', 'model-canonical', row.id));
        const value = node('span', 'model-value', formatCompact(row.value)); value.title = formatNumber(row.value) + ' ' + measure();
        line.append(label, value, node('span', 'model-share', formatShare(row.share))); button.append(line, bar(row.value, maximum));
        button.addEventListener('click', () => setModel(row.id, true)); li.append(button); list.append(li);
      });
      el('ranking-empty').hidden = ranking.rows.length !== 0;
    }
    function renderBreakdown() {
      const model = data.models.find(m => m.id === state.modelId), result = countryBreakdown(data, state.modelId, state.metric);
      el('selected-model-name').textContent = model?.name || state.modelId; el('selected-model-id').textContent = state.modelId;
      const selected = observation(data, state.modelId, state.country, state.metric), callout = el('selection-observation');
      callout.classList.toggle('is-missing', selected === null); callout.replaceChildren(node('span', '', groupName() + ' · ranking selection'), node('strong', '', selected === null ? 'Not separately reported' : formatNumber(selected) + ' ' + measure()));
      el('breakdown-total-label').textContent = 'All groups · ' + measure(); el('breakdown-total').textContent = formatCompact(result.total); el('breakdown-total').title = formatNumber(result.total);
      el('breakdown-caption').textContent = result.rows.length + ' reported groups. Share denominator: ' + formatNumber(result.total) + ' ' + measure() + '. ' + (result.total === 0 ? 'Shares are N/A because the reported total is zero.' : 'Bars are linear, relative to the largest group.');
      const list = el('country-breakdown'); list.replaceChildren(); const maximum = result.rows[0]?.value || 0;
      result.rows.forEach(row => {
        const li = node('li', 'country-row' + (row.special ? ' is-special' : '')), line = node('div', 'country-line'), name = node('span', 'country-name', row.name);
        if (!row.special && row.name !== row.code) name.append(node('span', 'country-code', row.code));
        const value = node('span', 'country-value', formatCompact(row.value)); value.title = formatNumber(row.value) + ' ' + measure();
        line.append(name, value, node('span', 'country-share', formatShare(row.share))); li.append(line, bar(row.value, maximum)); list.append(li);
      });
    }
    function renderTrend() {
      const trend = recentTrend(data, state.metric), chart = el('recent-trend'); chart.replaceChildren();
      trend.rows.forEach(row => {
        const day = node('div', 'trend-day'), column = node('div', 'trend-column'), stick = node('span', 'trend-bar');
        stick.style.height = (trend.peak > 0 ? row.value / trend.peak * 100 : 0) + '%'; column.append(stick); column.setAttribute('aria-hidden', 'true');
        const value = node('span', 'trend-value', formatCompact(row.value)), date = node('time', '', dateLabel(row.date, true)); date.dateTime = row.date; value.title = formatNumber(row.value) + ' ' + measure();
        day.setAttribute('aria-label', dateLabel(row.date) + ': ' + formatNumber(row.value) + ' ' + measure()); day.append(column, value, date); chart.append(day);
      });
      const last = trend.rows[trend.rows.length - 1];
      el('trend-change').textContent = last && last.changeRatio != null ? (last.changeRatio >= 0 ? '+' : '−') + formatShare(Math.abs(last.changeRatio)) + ' ' + measure() + ' on ' + dateLabel(last.date, true) + ' versus the previous day' : 'Not separately reported';
    }
    try {
      const global = rankModels(data, ALL_COUNTRIES, 'tokens', Infinity);
      el('stat-models').textContent = formatNumber(global.modelCount);
      el('stat-tokens').textContent = formatCompact(global.denominator); el('stat-tokens').title = formatNumber(global.denominator) + ' tokens';
      const requests = rankModels(data, ALL_COUNTRIES, 'requests', Infinity).denominator;
      el('stat-requests').textContent = formatCompact(requests); el('stat-requests').title = formatNumber(requests) + ' requests';
      el('snapshot-date').textContent = dateLabel(data.date_utc) + ' · UTC day';
      buildCountryOptions(data).forEach(c => { const option = node('option', '', c.name + (c.code.length === 2 && c.name !== c.code ? ' (' + c.code + ')' : '')); option.value = c.code; el('country-select').append(option); });
      data.models.slice().sort((a, b) => compareID(a.name, b.name) || compareID(a.id, b.id)).forEach(model => { const option = node('option', '', model.name + ' · ' + model.id); option.value = model.id; el('model-select').append(option); });
      el('model-select').value = state.modelId;
      el('country-select').addEventListener('change', event => { state.country = event.target.value; state.page = 1; renderRanking(); renderBreakdown(); });
      el('model-select').addEventListener('change', event => setModel(event.target.value));
      doc.querySelectorAll('input[name=metric]').forEach(input => input.addEventListener('change', event => {
        if (!event.target.checked) return; state.metric = event.target.value; state.page = 1;
        el('metric-help').textContent = state.metric === 'tokens' ? 'Tokens include input and output.' : 'Requests are API calls, not unique users.';
        renderRanking(); renderBreakdown(); renderTrend();
      }));
      function changePage(delta, event) {
        state.page += delta; renderRanking();
        if (event.currentTarget.closest('.bottom-pagination')) el('ranking-title').scrollIntoView({ block: 'start', behavior: 'auto' });
      }
      doc.querySelectorAll('.page-prev').forEach(button => button.addEventListener('click', event => changePage(-1, event)));
      doc.querySelectorAll('.page-next').forEach(button => button.addEventListener('click', event => changePage(1, event)));
      if (data.generated_at_utc) el('snapshot-captured').textContent = 'Prepared ' + new Date(data.generated_at_utc).toISOString().replace('T', ' ').replace(/\.\d+Z$/, ' UTC') + '. Usage day: ' + data.date_utc + ' UTC.';
      renderRanking(); renderBreakdown(); renderTrend(); el('explorer-app').hidden = false; status.hidden = true;
    } catch (error) {
      status.textContent = 'The snapshot could not be displayed. Its counts have not been replaced with zeros.';
      if (typeof console !== 'undefined') console.error(error);
    }
  }
  return { DEFAULT_MODEL_ID, ALL_COUNTRIES, PAGE_SIZE, rankModels, paginate, countryBreakdown, observation, buildCountryOptions, recentTrend, formatNumber, formatCompact, formatShare, init };
});
