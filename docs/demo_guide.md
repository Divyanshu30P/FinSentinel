# UPI Shield - Hackathon Demonstration Script (3-5 Minutes)

**Target Event**: Arthaton – AI for Finance  
**Track**: Financial Cybersecurity & Scam Detection  

---

## Demo Agenda Overview

| Time | Stage | Action / Highlights |
|---|---|---|
| **0:00 – 0:30** | **Problem & Identity** | Introduce UPI Shield: Digital payment fraud landscape in India (1930 helpline statistics, fake collect requests, electricity SMS scams). |
| **0:30 – 1:15** | **Module 2: Phishing Detector** | Click "⚡ Electricity Bill Threat", run scan, show highlighted malicious spans, TF-IDF + Logistic Regression 99.4% ML score, and AI explanation. |
| **1:15 – 2:00** | **Module 1: Collect Scanner** | Click "Diwali Reward PIN Scam", explain that typing a UPI PIN *debits* money, show 92/100 High Risk assessment and clear safety steps. |
| **2:00 – 2:45** | **Module 3: Transaction Analyser** | Click "Load Demo Statement", demonstrate Isolation Forest & velocity detector catching the 2:41 AM 3-part bank drain. |
| **2:45 – 3:30** | **Dashboard & Audit Log** | Show unified activity charts, risk distribution donut, recent alerts, and individual detail modal in History. |
| **3:30 – 4:00** | **Architecture & Wrap-up** | Highlight explainability, Windows compatibility, lightweight 4GB RAM operation, and 100% test coverage. |

---

## Step-by-Step Script for the Presenter

### 1. Introduction (0:00 - 0:30)
> *"Namaste judges. India's UPI ecosystem processes over 14 billion transactions monthly. However, fraudsters increasingly target everyday users through social engineering: fake collect requests, phishing SMS, and account drain bursts. Introducing **UPI Shield: Detect. Analyse. Protect.** Built specifically for Indian payment scenarios with lightweight ML and explainable AI."*

### 2. Phishing Message Detection (0:30 - 1:15)
1. In the sidebar, click **Phishing Detector**.
2. Click the preset button: `⚡ Electricity Bill Threat`.
3. Point out the text: *"Dear Consumer, your electricity power will be disconnected tonight at 9:30 PM..."*
4. Click **Run AI Phishing Analysis**.
5. Show results:
   - **Risk Score**: 96/100 (HIGH RISK).
   - **NLP ML Confidence**: 99.4% Phishing.
   - **Visual Highlighting**: Show the red-highlighted phrases like `power will be disconnected` and the phishing URL.
   - **AI Contextual Explanation**: Explains that power boards never use personal mobile numbers for disconnection threats.

### 3. Fake UPI Collect Request Detection (1:15 - 2:00)
1. In sidebar, click **Collect Request Scanner**.
2. Click the preset button: `Diwali Reward PIN Scam`.
3. Point out the scam trap: Sender asks user to *"Enter UPI PIN to receive Rs 4999 cashback"*.
4. Click **Analyze Collect Request**.
5. Emphasize the core educational insight:
   - *"UPI PIN is exclusively for DEBITING funds. It is never required to receive money."*
   - Show the `CRITICAL` indicator override and the 92/100 High Risk score.

### 4. Suspicious Transaction Anomaly Detection (2:00 - 2:45)
1. In sidebar, click **Transaction Analyser**.
2. Click **Load Demo Statement**.
3. Point out the summary banner:
   - 24 total transactions scanned.
   - 3 severe anomalies detected.
4. Show the transactions table:
   - Normal daytime transactions (Swiggy, Groceries) are green (Low Risk).
   - The 3 rapid transactions at 2:41 AM totaling ₹94,998 are flagged with: `Isolation Forest Outlier`, `Late Night (1-5 AM)`, `Rapid Velocity (3 in 1hr)`.

### 5. Unified Dashboard & Audit History (2:45 - 3:30)
1. Click **Overview** in the sidebar.
2. Review the live Chart.js activity graph and threat risk distribution donut.
3. Review the Active Fraud Alerts.
4. Click **Analysis History** to demonstrate the full audit log, filters, and detail modal.

### 6. Technology & System Integrity (3:30 - 4:00)
1. Open terminal and run `python ml\evaluate.py` to show the genuine test set performance report (100% test accuracy on held-out samples).
2. Point out that the system runs smoothly on Windows with 4GB RAM without Docker or heavyweight infrastructure.
