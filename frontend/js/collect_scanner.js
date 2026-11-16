// UPI Shield - Module 1: Fake UPI Collect Request Detector
class CollectScannerController {
  constructor() {
    this.presets = {
      diwali_reward: {
        sender_name: "Diwali Cashback Desk",
        sender_vpa: "cashback.rewards@okhdfcbank",
        requested_amount: 4999.00,
        request_description: "Enter UPI PIN to receive Rs 4999 Diwali cashback into your account",
        expected: false,
        known: false,
        message: "Click accept and enter your 6-digit UPI PIN to claim reward."
      },
      olx_buyer: {
        sender_name: "Subedar R.K. Sharma (Indian Army)",
        sender_vpa: "advance.army.pay@okaxis",
        requested_amount: 15000.00,
        request_description: "Advance payment for Sofa on OLX. Enter PIN to verify deposit.",
        expected: false,
        known: false,
        message: "I am sending you army cantonment advance. Please accept collect request."
      },
      electricity_legit: {
        sender_name: "BSES Yamuna Power Ltd",
        sender_vpa: "billdesk@sbi",
        requested_amount: 1420.00,
        request_description: "Electricity Bill Payment CA# 102938475",
        expected: true,
        known: true,
        message: "Payment due for electricity consumption period Oct-Nov."
      }
    };
    this.init();
  }

  init() {
    const form = document.getElementById('form-collect-scanner');
    if (form) {
      form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
  }

  loadPreset(key) {
    const p = this.presets[key];
    if (!p) return;

    document.getElementById('collect-sender-name').value = p.sender_name;
    document.getElementById('collect-sender-vpa').value = p.sender_vpa;
    document.getElementById('collect-amount').value = p.requested_amount;
    document.getElementById('collect-description').value = p.request_description;
    document.getElementById('collect-expected').checked = p.expected;
    document.getElementById('collect-known').checked = p.known;
    document.getElementById('collect-message').value = p.message;

    window.app.showToast(`Loaded scenario: ${p.sender_name}`, 'info');
  }

  async handleScreenshotUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      window.app.showToast('Extracting text from screenshot via OCR...', 'info');
      const data = await window.app.apiRequest('/upload/screenshot', {
        method: 'POST',
        body: formData
      });

      if (data.extracted_text) {
        document.getElementById('collect-message').value = data.extracted_text;
        window.app.showToast(data.notice || 'Screenshot text successfully extracted!', 'success');
      }
    } catch (e) {
      // Error handled in apiRequest
    }
  }

  async handleSubmit(e) {
    e.preventDefault();

    const payload = {
      sender_name: document.getElementById('collect-sender-name').value.trim(),
      sender_vpa: document.getElementById('collect-sender-vpa').value.trim(),
      requested_amount: parseFloat(document.getElementById('collect-amount').value),
      request_description: document.getElementById('collect-description').value.trim(),
      expected_request: document.getElementById('collect-expected').checked,
      sender_known: document.getElementById('collect-known').checked,
      associated_message: document.getElementById('collect-message').value.trim()
    };

    const submitBtn = document.getElementById('btn-analyze-collect');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Analyzing Security Factors...`;
    if (window.lucide) lucide.createIcons();

    try {
      const res = await window.app.apiRequest('/fraud/analyze-collect-request', {
        method: 'POST',
        body: JSON.stringify(payload)
      });

      this.renderResult(res);
      window.app.showToast(`Assessment complete: ${res.risk_category} Risk`, res.risk_category === 'HIGH' ? 'error' : (res.risk_category === 'MEDIUM' ? 'info' : 'success'));
    } catch (err) {
      console.error(err);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i data-lucide="scan"></i> Analyze Collect Request`;
      if (window.lucide) lucide.createIcons();
    }
  }

  renderResult(res) {
    const box = document.getElementById('collect-result-box');
    box.classList.add('active');

    // Badge & Score
    const badge = document.getElementById('collect-risk-badge');
    badge.className = `risk-badge ${res.risk_category}`;
    badge.textContent = `${res.risk_category} RISK`;

    document.getElementById('collect-risk-score').innerHTML = `${res.risk_score} <span>/ 100</span>`;

    // Explanation
    document.getElementById('collect-explanation-text').textContent = res.explanation;

    // Indicators
    const indList = document.getElementById('collect-indicators-list');
    if (!res.detected_indicators || res.detected_indicators.length === 0) {
      indList.innerHTML = `<div style="font-size: 0.85rem; color: var(--text-muted);">No suspicious red flags triggered. Standard transaction profile.</div>`;
    } else {
      indList.innerHTML = res.detected_indicators.map(ind => `
        <div class="indicator-item ${ind.severity}">
          <div class="indicator-title">
            <span class="risk-badge ${ind.severity}" style="font-size: 0.68rem; padding: 2px 7px;">${ind.severity}</span>
            <span>${ind.title}</span>
          </div>
          <div class="indicator-desc">${ind.description}</div>
        </div>
      `).join('');
    }

    // Recommendations
    const recList = document.getElementById('collect-recommendations-list');
    recList.innerHTML = (res.safety_recommendations || []).map(r => `<li>${r}</li>`).join('');

    // Smooth scroll down to result
    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }
}

window.collectScanner = new CollectScannerController();
