from sqlalchemy import create_engine, Column, Integer, String, Boolean, ForeignKey, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///./healthcare.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Doctor(Base):
    __tablename__ = "doctors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    license_number = Column(String, unique=True)
    specialization = Column(String)
    is_approved = Column(Boolean, default=False)

class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    mobile = Column(String, unique=True, index=True)
    dob = Column(String)
    gender = Column(String)
    pincode = Column(String)
    # Encrypted fields
    medical_history = Column(Text, default="") 
    genetic_history = Column(Text, default="")
    habits = Column(Text, default="") # e.g., Smoking, Alcohol

class OTPRequest(Base):
    __tablename__ = "otp_requests"
    id = Column(Integer, primary_key=True, index=True)
    patient_mobile = Column(String)
    doctor_id = Column(Integer)
    otp_code = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

class Diagnosis(Base):
    __tablename__ = "diagnoses"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    symptoms = Column(String) # e.g., "Dengue", "Fever"
    pincode = Column(String)
    medications = Column(JSON) # List of dicts: {name, morning, afternoon, night}
    follow_up_date = Column(String)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

def init_db():
    Base.metadata.create_all(bind=engine)
