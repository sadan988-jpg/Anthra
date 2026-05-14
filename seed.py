import requests
import sys

BASE_URL = "http://127.0.0.1:8000"

def seed():
    print("Connecting to backend...")

    # 1. Register a dummy doctor (ignore if already exists)
    doc_data = {
        "name": "Dr. Demo",
        "email": "demo@hospital.com",
        "license_number": "LIC123456",
        "specialization": "Epidemiology"
    }
    res = requests.post(f"{BASE_URL}/register/doctor", json=doc_data)
    if res.status_code == 200:
        doc_id = res.json()["id"]
        print(f"[OK] Doctor registered (ID: {doc_id})")
    else:
        # Already exists - log in to get ID
        login_res = requests.post(f"{BASE_URL}/login/doctor", json={
            "email": "demo@hospital.com",
            "license_number": "LIC123456"
        })
        doc_id = login_res.json().get("id", 1)
        print(f"[OK] Doctor already exists (ID: {doc_id})")

    pincode = "560037"
    seeded = 0

    for i in range(1, 5):
        mobile = f"900000000{i}"

        # Register patient (skip if exists)
        pat_data = {
            "name": f"Demo Patient {i}",
            "mobile": mobile,
            "dob": "1985-06-15",
            "gender": "Male",
            "pincode": pincode,
            "genetic_history": "Diabetes",
            "habits": "Smoking"
        }
        pat_res = requests.post(f"{BASE_URL}/register/patient", json=pat_data)
        if pat_res.status_code == 200:
            patient_id = pat_res.json()["id"]
            print(f"[OK] Registered Patient {i} (mobile: {mobile})")
        else:
            # Patient exists - get from dashboard
            dash = requests.get(f"{BASE_URL}/patient/dashboard/{mobile}")
            if dash.status_code == 200:
                patient_id = dash.json()["patient"]["id"]
                print(f"[--] Patient {i} already exists (ID: {patient_id})")
            else:
                print(f"[ERR] Could not get patient {i}, skipping")
                continue

        # Add Dengue diagnosis
        diag_data = {
            "patient_id": patient_id,
            "doctor_id": doc_id,
            "symptoms": "Dengue",
            "pincode": pincode,
            "medications": [
                {"name": "Paracetamol 500mg", "morning": True, "afternoon": True, "night": True},
                {"name": "ORS Sachets", "morning": True, "afternoon": False, "night": True}
            ],
            "follow_up_date": "2026-05-21"
        }
        diag_res = requests.post(f"{BASE_URL}/diagnosis", json=diag_data)
        if diag_res.status_code == 200:
            seeded += 1
            print(f"[OK] Dengue diagnosis logged for Patient {i}")

    print("")
    print("=" * 50)
    print(f"DONE: Seeded {seeded} Dengue cases in Pincode {pincode}")
    print("INFO: Add ONE MORE case to trigger a RED outbreak alert on the map!")
    print("=" * 50)
    print("")
    print("Demo Login Credentials:")
    print(f"  Doctor  --> Email: demo@hospital.com | License: LIC123456")
    print(f"  Patient --> Mobile: 9000000001")
    print("")
    print("Open: http://127.0.0.1:8000/static/index.html")

if __name__ == "__main__":
    try:
        seed()
    except requests.exceptions.ConnectionError:
        print("[ERR] Cannot connect to backend.")
        print("      Run this first: uvicorn main:app --host 127.0.0.1 --port 8000")
    except Exception as e:
        print(f"[ERR] {e}")
