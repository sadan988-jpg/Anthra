from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import random
import datetime
from typing import List, Optional
from pydantic import BaseModel

from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import models
from database import SessionLocal
from security import encrypt_data, decrypt_data

# Initialize DB
models.init_db()

app = FastAPI(title="Secure Predictive Healthcare API")

# ─── Notification Vault ────────────────────────────────────────────────────────
# In-memory OTP store: { patient_id (int): { otp, doctor_id, created_at } }
# A real production system would use Redis or a DB table with TTL.
notification_vault: dict = {}

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# ─── NOTIFICATION VAULT (Simulation Mode) ──────────────────────────────────
# Stores pending OTPs for the Patient's JS Listener Agent to pick up.
notification_vault: dict = {}


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Pydantic Schemas
class DoctorCreate(BaseModel):
    name: str
    email: str
    license_number: str
    specialization: str

class PatientCreate(BaseModel):
    name: str
    mobile: str
    dob: str
    gender: str
    pincode: str
    genetic_history: str = ""
    habits: str = ""

class DiagnosisCreate(BaseModel):
    patient_id: int
    doctor_id: int
    symptoms: str
    pincode: str
    medications: List[dict]
    follow_up_date: str

class DoctorLogin(BaseModel):
    email: str
    license_number: str

# --- Endpoints ---

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")

# ── Notification Queue: Doctor requests access ─────────────────────────────────
@app.post("/request-access/{patient_id}")
def request_access(patient_id: int, doctor_id: int, db: Session = Depends(get_db)):
    """
    Doctor triggers an OTP push to the patient's dashboard.
    Generates a 6-digit OTP, stores it in the notification_vault,
    and logs the event. Patient's JS listener will poll and consume it.
    """
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    doctor = db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")

    otp = str(random.randint(100000, 999999))
    notification_vault[patient_id] = {
        "otp": otp,
        "doctor_id": doctor_id,
        "doctor_name": doctor.name,
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    # Simulation: Log the event (no real SMS call)
    db_otp = models.OTPRequest(
        patient_mobile=patient.mobile,
        doctor_id=doctor_id,
        otp_code=otp,
        is_active=True
    )
    db.add(db_otp)
    audit = models.AuditLog(
        event=f"Dr. {doctor.name} PUSHED Virtual SMS to {patient.mobile}"
    )
    db.add(audit)
    db.commit()

    return {"status": "queued", "patient_id": patient_id}


# ── Notification Queue: Patient polls and consumes OTP (one-time delivery) ──────
@app.get("/get-otp/{patient_id}")
def get_otp(patient_id: int):
    """
    Called by the patient's JS polling agent every 3 seconds.
    Returns the OTP if one is waiting, then DELETES it from the vault
    so it is only delivered ONCE (simulating an SMS push).
    Returns 204 No Content if nothing is pending.
    """
    if patient_id not in notification_vault:
        # Nothing pending — return empty 204
        from fastapi.responses import Response
        return Response(status_code=204)

    payload = notification_vault.pop(patient_id)  # consume and remove
    return {
        "otp": payload["otp"],
        "doctor_name": payload["doctor_name"],
        "created_at": payload["created_at"]
    }


# ── Predictive Alert Engine: Check outbreak for a specific pincode ──────────────
@app.get("/check-outbreak/{pincode}")
def check_outbreak(pincode: str, db: Session = Depends(get_db)):
    """
    Returns outbreak status for a single pincode.
    Flags an outbreak if >= 5 cases of the same symptom exist in that pincode.
    Used by the patient JS listener to show a dynamic red warning banner.
    """
    diagnoses = db.query(models.Diagnosis).filter(models.Diagnosis.pincode == pincode).all()

    symptom_counts: dict = {}
    for d in diagnoses:
        symptom_counts[d.symptoms] = symptom_counts.get(d.symptoms, 0) + 1

    active_outbreaks = [
        {"symptom": symptom, "count": count, "pincode": pincode}
        for symptom, count in symptom_counts.items()
        if count >= 5
    ]

    return {
        "pincode": pincode,
        "outbreak_detected": len(active_outbreaks) > 0,
        "outbreaks": active_outbreaks,
        "total_cases": len(diagnoses)
    }

@app.post("/register/doctor")
def register_doctor(doc: DoctorCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Doctor).filter(models.Doctor.email == doc.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_doc = models.Doctor(**doc.dict())
    db.add(db_doc)
    db.commit()
    db.refresh(db_doc)
    return db_doc

@app.post("/login/doctor")
def login_doctor(creds: DoctorLogin, db: Session = Depends(get_db)):
    doc = db.query(models.Doctor).filter(
        models.Doctor.email == creds.email,
        models.Doctor.license_number == creds.license_number
    ).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Doctor not found")
    # For hackathon demo: auto-approve on first login
    if not doc.is_approved:
        doc.is_approved = True
        db.commit()
        db.refresh(doc)
    audit = models.AuditLog(event=f"Dr. {doc.name} logged into the Doctor Portal")
    db.add(audit)
    db.commit()
    return {"id": doc.id, "name": doc.name, "email": doc.email, "specialization": doc.specialization, "is_approved": doc.is_approved}

@app.get("/doctors")
def list_doctors(db: Session = Depends(get_db)):
    return db.query(models.Doctor).all()

@app.post("/register/patient")
def register_patient(pat: PatientCreate, db: Session = Depends(get_db)):
    # Encrypt sensitive fields
    pat_data = pat.dict()
    pat_data["genetic_history"] = encrypt_data(pat.genetic_history)
    pat_data["habits"] = encrypt_data(pat.habits)
    
    db_pat = models.Patient(**pat_data)
    db.add(db_pat)
    db.commit()
    db.refresh(db_pat)
    return db_pat

@app.post("/otp/request")
def request_otp(mobile: str, doctor_id: int, db: Session = Depends(get_db)):
    otp = str(random.randint(100000, 999999))
    new_request = models.OTPRequest(patient_mobile=mobile, doctor_id=doctor_id, otp_code=otp)
    db.add(new_request)
    
    # Simulation Mode: Add to vault so the dashboard can see it
    # Find patient by mobile
    patient = db.query(models.Patient).filter(models.Patient.mobile == mobile).first()
    if patient:
        notification_vault[patient.id] = {
            "otp": otp,
            "doctor_id": doctor_id,
            "doctor_name": "Doctor " + str(doctor_id),
            "created_at": datetime.datetime.utcnow().isoformat()
        }
    
    # Log attempt
    audit = models.AuditLog(event=f"Doctor ID {doctor_id} requested Virtual SMS for {mobile}")
    db.add(audit)
    
    db.commit()
    return {"message": "Virtual SMS Sent"}

@app.get("/otp/verify")
def verify_otp(mobile: str, otp: str, doctor_id: int, db: Session = Depends(get_db)):
    request = db.query(models.OTPRequest).filter(
        models.OTPRequest.patient_mobile == mobile,
        models.OTPRequest.otp_code == otp,
        models.OTPRequest.is_active == True
    ).first()
    
    if not request:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    request.is_active = False
    
    # Access Granted: Log it
    patient = db.query(models.Patient).filter(models.Patient.mobile == mobile).first()
    audit = models.AuditLog(event=f"Doctor ID {doctor_id} ACCESS GRANTED to Patient {mobile}")
    db.add(audit)
    db.commit()
    
    # Return Decrypted Data
    return {
        "access_token": "temp_session_token_123",
        "patient_data": {
            "id": patient.id,
            "name": patient.name,
            "dob": patient.dob,
            "pincode": patient.pincode,
            "genetic_history": decrypt_data(patient.genetic_history),
            "habits": decrypt_data(patient.habits)
        }
    }

@app.post("/diagnosis")
def save_diagnosis(diag: DiagnosisCreate, db: Session = Depends(get_db)):
    new_diag = models.Diagnosis(**diag.dict())
    db.add(new_diag)
    db.commit()
    return {"status": "success"}

@app.get("/outbreaks")
def get_outbreaks(db: Session = Depends(get_db)):
    # Simple Engine: Count occurrences of symptoms in pincodes within last 7 days
    results = db.query(models.Diagnosis).all()
    pincode_map = {}
    for r in results:
        key = (r.pincode, r.symptoms)
        pincode_map[key] = pincode_map.get(key, 0) + 1
    
    outbreaks = []
    for (pincode, symptom), count in pincode_map.items():
        if count >= 5:
            outbreaks.append({"pincode": pincode, "symptom": symptom, "count": count})
    return outbreaks

@app.get("/risk_predict")
def predict_risk(patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.id == patient_id).first()
    # Simulated XAI Matrix
    # In a real app, this would be a loaded scikit-learn model
    age = 2026 - int(patient.dob.split("-")[0])
    genetic = decrypt_data(patient.genetic_history).lower()
    habits = decrypt_data(patient.habits).lower()
    
    risk_score = 10
    factors = {"Baseline": 10}
    
    if age > 50:
        risk_score += 25
        factors["Age Factor (>50)"] = 25
    if "diabetes" in genetic:
        risk_score += 35
        factors["Genetic Predisposition"] = 35
    if "smoking" in habits:
        risk_score += 20
        factors["Lifestyle Habit (Smoking)"] = 20
        
    return {
        "risk_percentage": min(risk_score, 100),
        "breakdown": factors
    }

@app.get("/audit_logs")
def get_logs(db: Session = Depends(get_db)):
    logs = db.query(models.AuditLog).order_by(models.AuditLog.timestamp.desc()).limit(20).all()
    return [
        {"id": l.id, "event": l.event, "timestamp": l.timestamp.isoformat() if l.timestamp else None}
        for l in logs
    ]

@app.get("/patient/dashboard/{mobile}")
def get_patient_dashboard(mobile: str, db: Session = Depends(get_db)):
    patient = db.query(models.Patient).filter(models.Patient.mobile == mobile).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    diagnoses = db.query(models.Diagnosis).filter(models.Diagnosis.patient_id == patient.id).all()
    otps = db.query(models.OTPRequest).filter(
        models.OTPRequest.patient_mobile == mobile,
        models.OTPRequest.is_active == True
    ).all()

    return {
        "patient": {
            "id": patient.id, "name": patient.name, "mobile": patient.mobile,
            "dob": patient.dob, "gender": patient.gender, "pincode": patient.pincode
        },
        "diagnoses": [
            {
                "id": d.id, "symptoms": d.symptoms, "pincode": d.pincode,
                "medications": d.medications, "follow_up_date": d.follow_up_date,
                "doctor_id": d.doctor_id,
                "timestamp": d.timestamp.isoformat() if d.timestamp else None
            } for d in diagnoses
        ],
        "active_otps": [
            {"id": o.id, "otp_code": o.otp_code, "doctor_id": o.doctor_id,
             "created_at": o.created_at.isoformat() if o.created_at else None}
            for o in otps
        ]
    }
