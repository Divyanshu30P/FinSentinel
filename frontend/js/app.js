// UPI Shield - Core Application & Routing Controller
const API_BASE = '/api';

class AppController {
  constructor() {
    this.token = localStorage.getItem('upi_shield_token') || '';
    this.currentUser = {
      username: 'Hackathon Judge',
      email: 'demo@upishield.local',
      is_demo: true
    };
    this.currentView = 'dashboard';
    this.init();
  }

  async init() {
    this.bindEvents();
    this.updateUserUI();
    // Default load dashboard
    this.switchView('dashboard');
  }

  bindEvents() {
    // Sidebar navigation clicks
    document.querySelectorAll('.nav-item').forEach(item => {
      item.addEventListener('click', (e) => {
        const view = item.getAttribute('data-view');
        if (view) this.switchView(view);
      });
    });

    // Reset demo data button
    const btnReset = document.getElementById('btn-reset-demo');
    if (btnReset) {
      btnReset.addEventListener('click', () => this.resetDemoData());
    }

    // Modal background click close
    document.querySelectorAll('.modal-overlay').forEach(modal => {
      modal.addEventListener('click', (e) => {
        if (e.target === modal) {
          modal.classList.remove('active');
        }
      });
    });
  }

  switchView(viewName) {
    this.currentView = viewName;

    // Update active nav item
    document.querySelectorAll('.nav-item').forEach(item => {
      item.classList.toggle('active', item.getAttribute('data-view') === viewName);
    });

    // Hide all view sections, show active
    document.querySelectorAll('.view-section').forEach(sec => {
      sec.classList.remove('active');
    });

    const targetSec = document.getElementById(`view-${viewName}`);
    if (targetSec) {
      targetSec.classList.add('active');
    }

    // Update page title
    const titles = {
      'dashboard': 'Security Overview',
      'collect-scanner': 'Fake UPI Collect Scanner',
      'phishing-detector': 'Phishing & Scam Detector',
      'transaction-analyser': 'Transaction Anomaly Analyser',
      'fraud-alerts': 'Active Fraud Alerts',
      'analysis-history': 'Security Analysis History',
      'security-insights': 'Security Insights & Education',
      'settings-view': 'Platform Status & Settings'
    };
    const titleEl = document.getElementById('current-page-title');
    if (titleEl) titleEl.textContent = titles[viewName] || 'Dashboard';

    // Refresh lucide icons
    if (window.lucide) {
      setTimeout(() => lucide.createIcons(), 50);
    }

    // Trigger view-specific data loads
    if (viewName === 'dashboard' && window.dashboard) {
      window.dashboard.loadDashboard();
    } else if (viewName === 'fraud-alerts' && window.dashboard) {
      window.dashboard.loadAlertsView();
    } else if (viewName === 'analysis-history' && window.historyManager) {
      window.historyManager.loadHistory();
    }
  }

  async apiRequest(endpoint, options = {}) {
    const headers = options.headers || {};
    if (this.token) {
      headers['Authorization'] = `Bearer ${this.token}`;
    }
    if (!(options.body instanceof FormData) && !headers['Content-Type']) {
      headers['Content-Type'] = 'application/json';
    }

    try {
      const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        headers
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP Error ${response.status}`);
      }

      return await response.json();
    } catch (err) {
      console.error(`API Error on ${endpoint}:`, err);
      this.showToast(err.message || 'Network request failed', 'error');
      throw err;
    }
  }

  updateUserUI() {
    const nameEl = document.getElementById('user-display-name');
    const avatarEl = document.getElementById('user-avatar-initials');
    if (nameEl) nameEl.textContent = this.currentUser.username;
    if (avatarEl) {
      const parts = this.currentUser.username.split(' ');
      const initials = parts.map(p => p[0]).join('').slice(0, 2).toUpperCase();
      avatarEl.textContent = initials || 'US';
    }
  }

  async resetDemoData() {
    try {
      this.showToast('Resetting demo baseline data...', 'info');
      await this.apiRequest('/dashboard/reset-demo', { method: 'POST' });
      this.showToast('Demo data successfully restored to baseline!', 'success');
      if (window.dashboard) window.dashboard.loadDashboard();
      if (window.historyManager) window.historyManager.loadHistory();
    } catch (err) {
      // toast shown in apiRequest
    }
  }

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <i data-lucide="${type === 'success' ? 'check-circle' : (type === 'error' ? 'alert-triangle' : 'info')}" style="width: 18px; height: 18px;"></i>
      <span style="font-size: 0.88rem;">${message}</span>
    `;
    container.appendChild(toast);
    if (window.lucide) lucide.createIcons();

    setTimeout(() => {
      toast.style.opacity = '0';
      toast.style.transform = 'translateX(100%)';
      toast.style.transition = 'all 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  }

  openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.add('active');
  }

  closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) modal.classList.remove('active');
  }
}

// Global App Instance
window.app = new AppController();
