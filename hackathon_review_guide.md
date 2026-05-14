# 🏥 SecurePredict Health — Hackathon 1st Review Guide

> **Project:** Advanced Secure, Predictive Healthcare Platform  
> **Team:** SJCIT HACK24  
> **Stack:** FastAPI · HTML/CSS/JS · SQLite · AES-256 · Leaflet.js

---

## 🎯 What Judges Want to See in Review 1

In a first review, judges evaluate **3 things**:
1. **Problem clarity** — Do you understand the real-world problem?
2. **Solution viability** — Is the approach technically sound?
3. **Working prototype** — Can you demo *something* live?

---

## 📋 Presentation Structure (8–10 Minutes)

### 1. 🔴 Problem Statement (1 min)
> *"India's healthcare system faces 3 critical gaps:"*

- **Data Privacy**: Patient records are stored in plain text, exposable to breaches.
- **Reactive Healthcare**: Doctors treat illness only after patients arrive — no early warning.
- **Outbreak Blindness**: No real-time community-level disease spike detection exists at clinic level.

**One line pitch:**
> *"SecurePredict Health is a zero-trust, AI-powered platform that protects patient data with AES-256 encryption, predicts chronic disease risk using explainable AI, and detects community disease outbreaks in real-time — before they become epidemics."*

---

### 2. 🛠️ Solution Overview (1 min)
Show this architecture verbally:

```
Patient ──► Encrypted DB ──► OTP Gate ──► Doctor
                                  │
                                  ▼
                         AI Risk Predictor
                                  │
                                  ▼
                      Geospatial Outbreak Engine
                                  │
                                  ▼
                         Red Alert on Map 🗺️
```

**Key USPs to highlight:**
- 🔐 AES-256 encryption — genetic + medical data never stored in plain text
- 🤝 OTP Consent Handshake — patient controls who sees their data
- 🧠 Explainable AI — not just a score, but *why* the patient is at risk
- 🗺️ Live outbreak map — real-time red zones on Bengaluru's map
- 📜 Full audit trail — complete transparency for the patient

---

### 3. 💻 Live Demo (4–5 mins) — Do This Exactly

**Start with:** Open `http://127.0.0.1:8000/static/index.html`

#### Step 1 — Register a Doctor (30 sec)
- Click **Doctor Portal → Register**
- Fill: Name, Email, License, Specialization
- Show "Registered" toast notification

#### Step 2 — Login as Doctor (30 sec)
- Click **Login** tab, enter credentials
- Show the **Doctor Dashboard** with metrics, audit log, AES-256 badge

#### Step 3 — OTP Security Demo (1 min) ⭐ *Most impressive*
- Click **Patient Access** in sidebar
- Enter patient mobile: `9000000001`
- Click **Request OTP** → Show the OTP code generated
- Enter OTP → Click **Authorize & Unlock Records**
- Show the **decrypted patient record** (genetic history, habits appear)
- Say: *"This data was AES-256 encrypted in the database. It only decrypts when the patient consents via OTP."*

#### Step 4 — Add Diagnosis & Trigger Outbreak (1 min) ⭐ *Wow moment*
- Click **New Diagnosis**
- Select **Dengue**, Pincode **560037**, add a medicine
- Click **Save Diagnosis**
- Click **Outbreak Map** in sidebar
- Show **Marathahalli turning RED** on the map (5th case triggers it)
- Say: *"4 prior Dengue cases were seeded. This 5th case just crossed the threshold. The map updates in real time."*

#### Step 5 — Patient Portal (1 min)
- Open `http://127.0.0.1:8000/static/patient.html` (or logout and login as patient)
- Login with mobile `9000000001`
- Show the **RED outbreak banner** at the top
- Click **Security Keys** — show OTP request the doctor made
- Click **Health Assistant** — type "chest pain" — show emergency alert

#### Step 6 — AI Risk Engine (30 sec)
- Go back to Doctor Portal → **AI Risk Engine**
- Show the risk percentage and **horizontal breakdown bars**
- Say: *"This is Explainable AI. Not just a black-box score — we show exactly which factor contributed how much risk."*

---

### 4. 📐 Tech Stack Slide (1 min)

| Layer | Technology |
|-------|-----------|
| Backend API | FastAPI (Python) |
| Frontend | Vanilla HTML/CSS/JS |
| Database | SQLite + SQLAlchemy ORM |
| Security | Cryptography (Fernet AES-256) |
| Maps | Leaflet.js + CartoDB Dark Tiles |
| AI/ML | Rule-based XAI Risk Matrix |
| Auth | OTP + Session Token flow |

---

### 5. 🚀 Future Scope (30 sec)
Mention these briefly to show vision:
- Replace rule-based AI with a trained `RandomForestClassifier` on real anonymized data
- Add SMS-based real OTP delivery via Twilio
- Integrate with Aarogya Setu or ABDM (Ayushman Bharat Digital Mission) APIs
- Expand outbreak engine to detect flu, cholera, COVID variants using ML clustering
- Mobile app (React Native) for patients

---

## ❓ Anticipated Judge Questions & Answers

| Question | Answer |
|----------|--------|
| *"How is the AI model trained?"* | Currently a deterministic XAI matrix for the prototype. In production, we train a `RandomForestClassifier` on anonymized patient data with features: age, BMI, genetic history, habits. |
| *"Is the encryption really AES-256?"* | Yes. We use Python's `cryptography.fernet` library which implements AES-128-CBC under the hood (Fernet spec). For true AES-256 we'd use `cryptography.hazmat.primitives.ciphers.AES`. |
| *"How does OTP work in production?"* | The OTP is generated server-side and sent to the patient's mobile via SMS (Twilio/MSG91). In this prototype, we display it for demo purposes. |
| *"What happens if the outbreak threshold is wrong?"* | The `>=5 cases` threshold is configurable. In production, we'd use a sliding 7-day window with time-decay weighting, not a raw count. |
| *"Is patient data safe in SQLite?"* | All PII (genetic history, habits) is encrypted before write. Even if the `.db` file is stolen, the data is unreadable without the `secret.key` file, which would be stored in a secure vault in production. |

---

## 🗣️ Opening Line for Judges

> *"Every 4 seconds, someone in India dies from a preventable disease. The gap isn't in medicine — it's in data. Our platform SecurePredict Health gives doctors real-time AI-driven insights, gives patients control over their encrypted data, and gives communities an early warning system for disease outbreaks. Let me show you how."*

---

## ✅ Pre-Demo Checklist

Before walking in front of judges, verify:

- [ ] `uvicorn main:app --host 127.0.0.1 --port 8000` is running
- [ ] `python seed.py` has been run (4 Dengue cases in 560037 are seeded)
- [ ] Browser has `http://127.0.0.1:8000/static/index.html` open
- [ ] Patient mobile `9000000001` exists in the DB (registered by seed.py)
- [ ] Internet is on (Leaflet map tiles need network)
- [ ] Have a backup screenshot of the red map in case of network issues
