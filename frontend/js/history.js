// UPI Shield - Analysis History & Audit Log Controller
class HistoryController {
  constructor() {
    this.historyRecords = [];
    this.init();
  }

  init() {
    const searchInput = document.getElementById('hist-search-input');
    const catFilter = document.getElementById('hist-category-filter');
    const riskFilter = document.getElementById('hist-risk-filter');
    const btnClear = document.getElementById('btn-clear-history');

    if (searchInput) searchInput.addEventListener('input', () => this.loadHistory());
    if (catFilter) catFilter.addEventListener('change', () => this.loadHistory());
    if (riskFilter) riskFilter.addEventListener('change', () => this.loadHistory());
    if (btnClear) btnClear.addEventListener('click', () => this.clearHistory());
  }

  async loadHistory() {
    const search = document.getElementById('hist-search-input')?.value || '';
    const category = document.getElementById('hist-category-filter')?.value || 'ALL';
    const risk = document.getElementById('hist-risk-filter')?.value || 'ALL';

    const params = new URLSearchParams();
    if (search.trim()) params.append('search', search.trim());
    if (category !== 'ALL') params.append('category', category);
    if (risk !== 'ALL') params.append('risk', risk);

    try {
      const records = await window.app.apiRequest(`/fraud/history?${params.toString()}`);
      this.historyRecords = records;
      this.renderHistoryTable(records);
    } catch (e) {
      console.warn('Failed to load history:', e);
    }
  }

  renderHistoryTable(records) {
    const tbody = document.getElementById('history-table-body');
    if (!tbody) return;

    if (!records || records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-secondary); padding: 32px;">No historical analyses found matching the filter criteria.</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map(r => {
      const catLabel = r.category === 'COLLECT_REQUEST' ? 'Collect Request' : (r.category === 'PHISHING_MESSAGE' ? 'Phishing Message' : 'Transaction Scan');
      return `
        <tr>
          <td><span style="font-weight: 600; font-size: 0.82rem; color: var(--accent-secondary);">${catLabel}</span></td>
          <td style="max-width: 320px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${r.input_summary}</td>
          <td><span class="risk-badge ${r.risk_category}" style="font-size: 0.72rem; padding: 2px 8px;">${r.risk_category}</span></td>
          <td style="font-weight: 700;">${r.risk_score}/100</td>
          <td style="font-size: 0.8rem; color: var(--text-secondary);">${r.created_at}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="window.historyManager.viewAnalysisDetail('${r.id}')">
              <i data-lucide="eye" style="width: 13px; height: 13px;"></i> Details
            </button>
          </td>
        </tr>
      `;
    }).join('');

    if (window.lucide) lucide.createIcons();
  }

  async viewAnalysisDetail(analysisId) {
    try {
      const detail = await window.app.apiRequest(`/fraud/${analysisId}`);
      
      const catMap = {
        'COLLECT_REQUEST': 'Fake Collect Request Analysis',
        'PHISHING_MESSAGE': 'Phishing & Scam Message Analysis',
        'TRANSACTION_ANOMALY': 'Transaction Behavioral Analysis'
      };

      document.getElementById('modal-detail-category').textContent = catMap[detail.category] || detail.category;
      document.getElementById('modal-detail-title').textContent = detail.input_summary;
      
      const badge = document.getElementById('modal-detail-badge');
      badge.className = `risk-badge ${detail.risk_category}`;
      badge.textContent = `${detail.risk_category} RISK`;

      document.getElementById('modal-detail-score').innerHTML = `${detail.risk_score} <span>/ 100</span>`;
      document.getElementById('modal-detail-explanation').textContent = detail.explanation;

      // Indicators
      const indEl = document.getElementById('modal-detail-indicators');
      if (!detail.detected_indicators || detail.detected_indicators.length === 0) {
        indEl.innerHTML = `<div style="font-size: 0.82rem; color: var(--text-muted);">No threat indicators detected.</div>`;
      } else {
        indEl.innerHTML = detail.detected_indicators.map(ind => `
          <div class="indicator-item ${ind.severity}">
            <div class="indicator-title">
              <span class="risk-badge ${ind.severity}" style="font-size: 0.65rem; padding: 2px 6px;">${ind.severity}</span>
              <span>${ind.title}</span>
            </div>
            <div class="indicator-desc">${ind.description}</div>
          </div>
        `).join('');
      }

      // Recommendations
      const recEl = document.getElementById('modal-detail-recommendations');
      recEl.innerHTML = (detail.safety_recommendations || []).map(r => `<li>${r}</li>`).join('');

      window.app.openModal('modal-analysis-detail');
      if (window.lucide) lucide.createIcons();
    } catch (e) {
      // Handled in apiRequest
    }
  }

  async clearHistory() {
    if (!confirm('Are you sure you want to clear your fraud analysis history? This action cannot be undone.')) {
      return;
    }

    try {
      await window.app.apiRequest('/fraud/history', { method: 'DELETE' });
      window.app.showToast('Analysis history cleared successfully', 'success');
      this.loadHistory();
      if (window.dashboard) window.dashboard.loadDashboard();
    } catch (e) {
      // Handled in apiRequest
    }
  }
}

window.historyManager = new HistoryController();
