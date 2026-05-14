# 🏥 SecurePredict Health
### *Advanced Secure & Predictive Healthcare Analytics Platform*

**SecurePredict Health** is a zero-trust, AI-powered healthcare ecosystem designed to bridge the gap between patient privacy and proactive community health. It combines **AES-256 encryption** for medical records, **Explainable AI (XAI)** for chronic disease risk prediction, and **Geospatial Analytics** for real-time disease outbreak detection.

---

## 🚀 Key Features

### 1. 🔐 Zero-Trust Data Privacy
- **AES-256 Encryption**: Sensitive patient data (genetic history, habits, prescriptions) is encrypted before storage.
- **OTP Handshake**: Doctors can only access patient records after a secure OTP verification, simulating a real-world consent flow.
- **Audit Trails**: Every data access event is logged in a tamper-evident audit trail for both doctors and patients to see.

### 2. 🧠 Explainable AI (XAI) Risk Engine
- **Risk Prediction**: Analyzes lifestyle habits and genetic history to predict chronic disease risks.
- **The "Why" Factor**: Instead of a black-box score, it provides a horizontal breakdown of which specific factors contributed to the risk.

### 3. 🗺️ Predictive Outbreak Mapping
- **Geospatial Surveillance**: Monitors diagnosis trends across pincodes in real-time.
- **Auto-Alert System**: Dynamically flags areas on an interactive map using **Leaflet.js** when a disease threshold is crossed.
- **Patient Alerts**: Automatically injects emergency warning banners into the dashboards of patients living in flagged zones.

### 4. 📱 Virtual SMS Simulation
- A custom "Notification Vault" and "Listener Agent" system that pushes mock WhatsApp/SMS notifications to the patient's device for demo purposes.

---

## 🛠️ Tech Stack

- **Backend**: Python, FastAPI, Uvicorn
- **Database**: SQLite, SQLAlchemy ORM
- **Security**: Cryptography (AES-256 / Fernet), OTP Vaulting
- **Frontend**: Premium HTML5, CSS3 (Glassmorphism), Vanilla JavaScript
- **Maps**: Leaflet.js, CartoDB Dark Matter
- **Data Validation**: Pydantic

---

## ⚡ Quick Start

### 1. Clone & Install
```bash
git clone https://github.com/sadan988-jpg/Anthra.git
cd Anthra
pip install -r requirements.txt
```

### 2. Run the Backend
```bash
uvicorn main:app --reload
```

### 3. Seed Demo Data
In a new terminal:
```bash
python seed.py
```

---

## 🧑‍🔬 Demo Credentials
- **Doctor**: `demo@hospital.com` | License: `LIC123456`
- **Patient**: Mobile `9000000001` (Use this for the OTP Handshake demo)
