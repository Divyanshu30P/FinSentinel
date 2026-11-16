// UPI Shield - Dashboard & Analytics Controller
class DashboardController {
  constructor() {
    this.activityChart = null;
    this.riskChart = null;
    this.init();
  }

  init() {
    // Initial fetch when document is ready
    setTimeout(() => this.loadDashboard(), 100);
  }

  async loadDashboard() {
    try {
      const summary = await window.app.apiRequest('/dashboard/summary');
      this.updateStats(summary);
      this.renderRecentTable(summary.recent_analyses);
      this.updateAlertBadge(summary.recent_alerts);
      await this.loadAnalyticsCharts();
    } catch (err) {
      console.error('Failed to load dashboard:', err);
    }
  }

  updateStats(summary) {
    document.getElementById('stat-total-analyzed').textContent = summary.total_analyses;
    document.getElementById('stat-high-risk').textContent = summary.high_risk_count;
    document.getElementById('stat-medium-risk').textContent = summary.medium_risk_count;
    document.getElementById('stat-transactions').textContent = summary.transactions_count;
  }

  updateAlertBadge(alerts) {
    const badge = document.getElementById('nav-alert-badge');
    if (badge) {
      const unreadCount = alerts ? alerts.length : 0;
      badge.textContent = unreadCount;
      badge.style.display = unreadCount > 0 ? 'inline-block' : 'none';
    }
  }

  renderRecentTable(records) {
    const tbody = document.getElementById('dashboard-recent-table');
    if (!tbody) return;

    if (!records || records.length === 0) {
      tbody.innerHTML = `<tr><td colspan="6" style="text-align: center; color: var(--text-secondary); padding: 20px;">No security scans recorded yet.</td></tr>`;
      return;
    }

    tbody.innerHTML = records.map(r => {
      const catLabel = r.category === 'COLLECT_REQUEST' ? 'Collect Scanner' : (r.category === 'PHISHING_MESSAGE' ? 'Phishing Detector' : 'Transaction Scan');
      const badgeClass = r.risk_category;
      return `
        <tr>
          <td><span style="font-weight: 600; font-size: 0.82rem; color: var(--accent-secondary);">${catLabel}</span></td>
          <td style="max-width: 300px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${r.input_summary}</td>
          <td><span class="risk-badge ${badgeClass}" style="font-size: 0.72rem; padding: 3px 10px;">${r.risk_category}</span></td>
          <td style="font-weight: 700;">${r.risk_score}/100</td>
          <td style="font-size: 0.8rem; color: var(--text-secondary);">${r.created_at}</td>
          <td>
            <button class="btn btn-secondary btn-sm" onclick="window.historyManager.viewAnalysisDetail('${r.id}')">
              <i data-lucide="eye" style="width: 13px; height: 13px;"></i> View
            </button>
          </td>
        </tr>
      `;
    }).join('');

    if (window.lucide) lucide.createIcons();
  }

  async loadAnalyticsCharts() {
    try {
      const dist = await window.app.apiRequest('/analytics/risk-distribution');
      this.renderActivityChart(dist.timeline);
      this.renderRiskChart(dist.high_risk, dist.medium_risk, dist.low_risk);
    } catch (e) {
      console.warn('Analytics charts error:', e);
    }
  }

  renderActivityChart(timeline) {
    const ctx = document.getElementById('chart-activity');
    if (!ctx) return;

    const labels = timeline ? timeline.map(t => t.date) : ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    const data = timeline ? timeline.map(t => t.count) : [2, 4, 3, 5, 8, 4, 6];

    if (this.activityChart) {
      this.activityChart.destroy();
    }

    this.activityChart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: labels,
        datasets: [{
          label: 'Threat Scans & Detections',
          data: data,
          borderColor: '#35C99A',
          backgroundColor: 'rgba(53, 201, 154, 0.1)',
          fill: true,
          tension: 0.35,
          borderWidth: 2,
          pointBackgroundColor: '#35C99A',
          pointRadius: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94A3B8', font: { size: 11 } }
          },
          y: {
            beginAtZero: true,
            grid: { color: 'rgba(255, 255, 255, 0.05)' },
            ticks: { color: '#94A3B8', stepSize: 1, font: { size: 11 } }
          }
        }
      }
    });
  }

  renderRiskChart(high, medium, low) {
    const ctx = document.getElementById('chart-risk');
    if (!ctx) return;

    if (this.riskChart) {
      this.riskChart.destroy();
    }

    const total = high + medium + low;
    const data = total > 0 ? [high, medium, low] : [3, 2, 5];

    this.riskChart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['High Risk', 'Medium Risk', 'Low Risk'],
        datasets: [{
          data: data,
          backgroundColor: ['#F05D65', '#F4B942', '#35C99A'],
          borderWidth: 0,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { color: '#F1F5F9', font: { size: 11 }, padding: 16 }
          }
        }
      }
    });
  }

  async loadAlertsView() {
    const container = document.getElementById('alerts-list-container');
    if (!container) return;

    try {
      const summary = await window.app.apiRequest('/dashboard/summary');
      const alerts = summary.recent_alerts || [];

      if (alerts.length === 0) {
        container.innerHTML = `<div style="text-align: center; color: var(--text-secondary); padding: 32px;">No active fraud alerts. Your system is safe.</div>`;
        return;
      }

      container.innerHTML = alerts.map(a => `
        <div class="card" style="border-left: 4px solid ${a.risk_category === 'HIGH' ? 'var(--danger)' : 'var(--warning)'}; padding: 18px;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start;">
            <div>
              <div style="font-weight: 700; font-size: 1rem; color: var(--text-primary);">${a.title}</div>
              <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 4px;">${a.description}</div>
            </div>
            <span class="risk-badge ${a.risk_category}" style="font-size: 0.72rem; padding: 2px 8px;">${a.risk_category}</span>
          </div>
          <div style="margin-top: 10px; font-size: 0.75rem; color: var(--text-muted);">${a.created_at}</div>
        </div>
      `).join('');

      if (window.lucide) lucide.createIcons();
    } catch (e) {
      console.warn('Failed to load alerts view:', e);
    }
  }
}

window.dashboard = new DashboardController();
