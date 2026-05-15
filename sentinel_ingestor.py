import requests
import json
from sqlalchemy.orm import Session
from database import SessionLocal
import models
import datetime
import random

# District to Pincode mapping for Karnataka (Simplified for demo)
KARNATAKA_PINCODES = {
    "Bengaluru Urban": ["560001", "560037", "560066"],
    "Bengaluru Rural": ["562110", "562114"],
    "Mysuru": ["570001", "570010"],
    "Shivamogga": ["577201", "577204"], # High KFD risk area
    "Belagavi": ["590001", "590010"]
}

def fetch_nivedi_bulletin():
    """
    In a real-world scenario, this would use BeautifulSoup or Selenium 
    to parse bulletins from https://nivedi.res.in/Nadres_v2/.
    For this prototype, we simulate the parsed data based on NADRES v2 patterns.
    """
    print("Fetching ICAR-NIVEDI (NADRES v2) bulletins...")
    
    # Mocked data reflecting realistic zoonotic threats in Karnataka
    return [
        {"district": "Bengaluru Urban", "pathogen": "Avian Influenza", "risk": 0.85},
        {"district": "Shivamogga", "pathogen": "Kyasanur Forest Disease (KFD)", "risk": 0.92},
        {"district": "Belagavi", "pathogen": "Anthrax", "risk": 0.78},
        {"district": "Mysuru", "pathogen": "Avian Influenza", "risk": 0.45},
    ]

def ingest_sentinel_data():
    db = SessionLocal()
    try:
        bulletins = fetch_nivedi_bulletin()
        
        for item in bulletins:
            district = item["district"]
            pathogen = item["pathogen"]
            risk = item["risk"]
            
            pincodes = KARNATAKA_PINCODES.get(district, [])
            
            for pc in pincodes:
                # Update if exists, else create
                existing = db.query(models.AnimalDiseaseRisk).filter(
                    models.AnimalDiseaseRisk.pincode == pc,
                    models.AnimalDiseaseRisk.pathogen_type == pathogen
                ).first()
                
                if existing:
                    existing.risk_level = risk
                    existing.last_updated = datetime.datetime.utcnow()
                else:
                    new_risk = models.AnimalDiseaseRisk(
                        district=district,
                        pincode=pc,
                        pathogen_type=pathogen,
                        risk_level=risk
                    )
                    db.add(new_risk)
        
        db.commit()
        print(f"Successfully ingested {len(bulletins)} bulletins across mapped districts.")
    except Exception as e:
        print(f"Ingestion failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ingest_sentinel_data()
