// UPI Shield - Module 2: Financial Phishing & SMS Scam Detector
class PhishingDetectorController {
  constructor() {
    this.samples = {
      electricity: "Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM from the electricity office because your previous month bill was not updated. Please immediately contact our electricity officer at 9876543210 or update now: http://power-bill-disconnection-alert.site/pay",
      sbi_kyc: "Dear SBI User, your YONO SBI account has been blocked due to incomplete KYC. Please click here http://sbi-kyc-verify-portal.in/update to update your PAN and Aadhaar immediately to avoid permanent deactivation.",
      account_blocked: "Dear HDFC Customer, your NetBanking access is suspended today due to KYC non-compliance. Update your KYC within 24 hours at http://hdfc-netbanking-secure-login.xyz to restore services.",
      phonepe_reward: "Congratulations! You have received a cashback reward of Rs 4,999 on PhonePe. Click here to claim your reward into bank account: http://bit.ly/claim-phonepe-cashback and enter UPI PIN.",
      kbc_lottery: "KBC Season 16 Lucky Winner: Congratulations, your mobile number has won Rs 25,00,000 cash. Contact KBC manager at WhatsApp +91 98765 43210 to claim your prize.",
      anydesk_support: "Swiggy refund pending: We are unable to credit Rs 1,450. Please download customer care support tool http://anydesk-support-apk-download.net/app or share screen with our agent 9988776655.",
      legit_debit: "HDFC Bank: Rs 450.00 debited from A/C XX4129 on 15-Nov-2026 to VPA zomato@hdfcbank (UPI Ref no 987654123012). Available Bal: Rs 45,210.00. Call 18002586161 if not you.",
      legit_otp: "847291 is your secret OTP for transaction of Rs 620.00 at Blinkit. NEVER share this OTP with anyone, bank staff will never ask for OTP."
    };
    this.init();
  }

  init() {
    const form = document.getElementById('form-phishing-detector');
    if (form) {
      form.addEventListener('submit', (e) => this.handleSubmit(e));
    }
  }

  loadSample(key) {
    const text = this.samples[key];
    if (!text) return;

    document.getElementById('phishing-message-input').value = text;
    window.app.showToast(`Loaded preset: ${key.replace('_', ' ').toUpperCase()}`, 'info');
  }

  async pasteClipboard() {
    try {
      const text = await navigator.clipboard.readText();
      if (text) {
        document.getElementById('phishing-message-input').value = text;
        window.app.showToast('Pasted content from clipboard!', 'success');
      }
    } catch (e) {
      window.app.showToast('Clipboard access permission required or not supported in this browser.', 'error');
    }
  }

  async handleScreenshotUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      window.app.showToast('Extracting message text from screenshot via OCR...', 'info');
      const data = await window.app.apiRequest('/upload/screenshot', {
        method: 'POST',
        body: formData
      });

      if (data.extracted_text) {
        document.getElementById('phishing-message-input').value = data.extracted_text;
        const noticeEl = document.getElementById('ocr-notice-container');
        const textEl = document.getElementById('ocr-notice-text');
        if (noticeEl && textEl) {
          textEl.textContent = data.notice || 'OCR Extraction complete. You can review or edit the text above.';
          noticeEl.style.display = 'block';
        }
        window.app.showToast('Screenshot text extracted successfully!', 'success');
      }
    } catch (e) {
      // Error handled in apiRequest
    }
  }

  async handleSubmit(e) {
    e.preventDefault();

    const text = document.getElementById('phishing-message-input').value.trim();
    if (!text) return;

    const submitBtn = document.getElementById('btn-analyze-phishing');
    submitBtn.disabled = true;
    submitBtn.innerHTML = `<i data-lucide="loader-2" class="spin"></i> Running NLP & Heuristic Classifier...`;
    if (window.lucide) lucide.createIcons();

    try {
      const res = await window.app.apiRequest('/fraud/analyze-message', {
        method: 'POST',
        body: JSON.stringify({ message_text: text })
      });

      this.renderResult(res, text);
      window.app.showToast(`Analysis complete: ${res.risk_category} Risk`, res.risk_category === 'HIGH' ? 'error' : (res.risk_category === 'MEDIUM' ? 'info' : 'success'));
    } catch (err) {
      console.error(err);
    } finally {
      submitBtn.disabled = false;
      submitBtn.innerHTML = `<i data-lucide="sparkles"></i> Run AI Phishing Analysis`;
      if (window.lucide) lucide.createIcons();
    }
  }

  renderResult(res, originalText) {
    const box = document.getElementById('phishing-result-box');
    box.classList.add('active');

    // Badge & Score
    const badge = document.getElementById('phishing-risk-badge');
    badge.className = `risk-badge ${res.risk_category}`;
    badge.textContent = `${res.risk_category} RISK`;

    document.getElementById('phishing-risk-score').innerHTML = `${res.risk_score} <span>/ 100</span>`;

    // ML Confidence
    const mlConfEl = document.getElementById('phishing-ml-confidence');
    if (res.ml_confidence !== null && res.ml_confidence !== undefined) {
      mlConfEl.textContent = `NLP Classifier Confidence: ${(res.ml_confidence * 100).toFixed(1)}% (${res.ml_confidence >= 0.5 ? 'Phishing' : 'Legitimate'})`;
    } else {
      mlConfEl.textContent = `Rule Engine Analysis`;
    }

    // Highlighted Text Display
    const highlightBox = document.getElementById('phishing-highlight-box');
    let highlightedHtml = originalText;

    if (res.highlighted_spans && res.highlighted_spans.length > 0) {
      res.highlighted_spans.forEach(span => {
        if (!span || span.length < 2) return;
        const regex = new RegExp(`(${this.escapeRegex(span)})`, 'gi');
        highlightedHtml = highlightedHtml.replace(regex, `<span class="phish-highlight">$1</span>`);
      });
    }
    highlightBox.innerHTML = highlightedHtml;

    // Explanation
    document.getElementById('phishing-explanation-text').textContent = res.explanation;

    // Indicators
    const indList = document.getElementById('phishing-indicators-list');
    if (!res.detected_indicators || res.detected_indicators.length === 0) {
      indList.innerHTML = `<div style="font-size: 0.85rem; color: var(--text-muted);">No threat markers identified. Standard authentic pattern.</div>`;
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
    const recList = document.getElementById('phishing-recommendations-list');
    recList.innerHTML = (res.safety_recommendations || []).map(r => `<li>${r}</li>`).join('');

    box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
  }

  escapeRegex(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  }
}

window.phishingDetector = new PhishingDetectorController();
