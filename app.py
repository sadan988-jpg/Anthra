import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="SecurePredict Health", layout="wide", page_icon="🛡️")

# Custom CSS for Premium Look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #007BFF; color: white; }
    .stMetric { background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .card { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
    .banner { padding: 15px; border-radius: 8px; color: white; font-weight: bold; margin-bottom: 15px; }
    .banner-red { background-color: #ff4b4b; }
    .banner-green { background-color: #28a745; }
    </style>
""", unsafe_allow_html=True)

BASE_URL = "http://127.0.0.1:8000"

# Sidebar Navigation
st.sidebar.title("🛡️ SecurePredict")
role = st.sidebar.selectbox("Choose Portal", ["Doctor Portal", "Patient Portal"])

# --- Helper Functions ---
def get_outbreaks():
    try: return requests.get(f"{BASE_URL}/outbreaks").json()
    except: return []

# --- DOCTOR PORTAL ---
if role == "Doctor Portal":
    st.title("👨‍⚕️ Doctor Diagnostic Dashboard")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Search Patient", "Predictive Analytics", "Regional Health Map", "Early Warning Engine"])
    
    with tab1:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Patient Access")
            mobile = st.text_input("Patient Mobile Number")
            if st.button("Request OTP"):
                res = requests.post(f"{BASE_URL}/otp/request?mobile={mobile}&doctor_id=1")
                if res.status_code == 200:
                    st.success(f"OTP Sent! (Demo Code: {res.json()['otp']})")
            
            otp_input = st.text_input("Enter 6-Digit OTP", type="password")
            if st.button("Authorize Access"):
                res = requests.get(f"{BASE_URL}/otp/verify?mobile={mobile}&otp={otp_input}&doctor_id=1")
                if res.status_code == 200:
                    st.session_state.current_patient = res.json()["patient_data"]
                    st.success("Access Granted!")
                else:
                    st.error("Invalid OTP")
        
        with col2:
            if "current_patient" in st.session_state:
                p = st.session_state.current_patient
                st.subheader(f"Patient Profile: {p['name']}")
                c1, c2, c3 = st.columns(3)
                c1.metric("DOB", p["dob"])
                c2.metric("Pincode", p["pincode"])
                c3.metric("Gender", "Male") # Static for demo
                
                st.markdown("### 🔐 Decrypted Medical Data")
                st.info(f"**Genetic History:** {p['genetic_history']}")
                st.warning(f"**Lifestyle Habits:** {p['habits']}")
                
                st.markdown("---")
                st.subheader("New Diagnosis")
                symptoms = st.selectbox("Symptoms", ["Fever", "Dengue", "Hypertension", "Diabetes Checkup", "General Fatigue"])
                meds = st.text_area("Medications (JSON Format)", '[{"name": "Paracetamol", "morning": true, "afternoon": true, "night": true}]')
                follow_up = st.date_input("Follow-up Date")
                
                if st.button("Save Diagnosis"):
                    diag_data = {
                        "patient_id": p["id"],
                        "doctor_id": 1,
                        "symptoms": symptoms,
                        "pincode": p["pincode"],
                        "medications": [{}], # Simplified
                        "follow_up_date": str(follow_up)
                    }
                    requests.post(f"{BASE_URL}/diagnosis", json=diag_data)
                    st.success("Diagnosis Logged & Community Data Updated!")

    with tab2:
        if "current_patient" in st.session_state:
            st.subheader("🧠 XAI Chronic Risk Prediction")
            res = requests.get(f"{BASE_URL}/risk_predict?patient_id={st.session_state.current_patient['id']}")
            if res.status_code == 200:
                data = res.json()
                st.write(f"Aggregate Risk Score: **{data['risk_percentage']}%**")
                
                # Plotly Bar Chart for XAI
                breakdown = data["breakdown"]
                df_xai = pd.DataFrame(list(breakdown.items()), columns=["Factor", "Weight"])
                fig = px.bar(df_xai, x="Weight", y="Factor", orientation='h', title="Why the AI flagged this patient:")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please authorize a patient record first.")

    with tab3:
        st.subheader("📍 Real-time Geospatial Outbreak Engine")
        outbreaks = get_outbreaks()
        
        # Bengaluru Center
        m = folium.Map(location=[12.9716, 77.5946], zoom_start=12)
        
        # Pincode Mapping (Simplified for demo)
        pincode_coords = {
            "560001": [12.9716, 77.5946], # MG Road
            "560037": [12.9600, 77.7100], # Marathahalli
            "560066": [12.9667, 77.7500], # Whitefield
        }
        
        for pc, coords in pincode_coords.items():
            is_outbreak = any(o["pincode"] == pc for o in outbreaks)
            color = "red" if is_outbreak else "green"
            radius = 1000 if is_outbreak else 500
            
            folium.Circle(
                location=coords,
                radius=radius,
                popup=f"Pincode: {pc} - {'🚨 OUTBREAK DETECTED' if is_outbreak else 'Normal'}",
                color=color,
                fill=True,
                fill_color=color
            ).add_to(m)
        
        st_folium(m, width=1000, height=500)

    with tab4:
        st.subheader("🧠 Early Warning Outbreak Engine (AI Driven)")
        st.info("This engine aggregates real-time anomalies from non-invasive patient vitals (BVP) and respiratory cough analysis.")
        
        preds = requests.get(f"{BASE_URL}/api/v1/aggregation/outbreak-status").json()
        human_preds = preds.get("human_predictions", [])
        
        if not human_preds:
            st.success("No significant anomaly clusters detected in the last 48 hours.")
        else:
            col1, col2 = st.columns([2, 1])
            with col1:
                df_preds = pd.DataFrame(human_preds)
                st.table(df_preds)
                
                # Visualizing anomaly density
                fig = px.bar(df_preds, x="pincode", y="anomaly_density", color="risk_level", 
                             title="Localized Anomaly Density by Pincode",
                             color_discrete_map={"High": "red", "Medium": "orange", "Low": "green"})
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Map for early warning
                m2 = folium.Map(location=[12.9716, 77.5946], zoom_start=11)
                for p in human_preds:
                    coords = pincode_coords.get(p["pincode"], [12.9716, 77.5946])
                    color = "red" if p["risk_level"] == "High" else "orange" if p["risk_level"] == "Medium" else "green"
                    folium.Marker(
                        location=coords,
                        popup=f"Risk: {p['risk_level']} - Density: {p['anomaly_density']}",
                        icon=folium.Icon(color=color)
                    ).add_to(m2)
                st_folium(m2, width=400, height=400)

# --- PATIENT PORTAL ---
else:
    st.title("🛡️ My Patient Health Portal")
    
    mobile_login = st.sidebar.text_input("Enter Mobile to View Dashboard", value="9000000001")
    if mobile_login:
        res = requests.get(f"{BASE_URL}/patient/dashboard/{mobile_login}")
        if res.status_code == 200:
            data = res.json()
            patient = data["patient"]
            
            # --- OUTBREAK ALERT BANNER ---
            outbreaks = get_outbreaks()
            is_in_danger = any(o["pincode"] == patient["pincode"] for o in outbreaks)
            if is_in_danger:
                st.markdown(f"""<div class="banner banner-red">⚠️ EARLY WARNING: An outbreak of {outbreaks[0]['symptom']} has been detected in your area ({patient['pincode']}). Stay safe!</div>""", unsafe_allow_html=True)
            else:
                st.markdown(f"""<div class="banner banner-green">✅ Your area ({patient['pincode']}) is currently safe. No active outbreaks.</div>""", unsafe_allow_html=True)

            col_a, col_b = st.columns([2, 1])
            
            with col_a:
                st.subheader("💊 Medication Timeline")
                # Simple schedule simulation
                st.checkbox("Morning: Paracetamol (500mg) - Done", value=True)
                st.checkbox("Afternoon: Paracetamol (500mg)")
                st.checkbox("Night: Paracetamol (500mg)")
                
                st.markdown("### 📋 Recent Diagnoses")
                for diag in data["diagnoses"]:
                    with st.expander(f"Visit on {diag['timestamp'][:10]} - {diag['symptoms']}"):
                        st.write(f"Doctor ID: {diag['doctor_id']}")
                        st.write(f"Follow up: {diag['follow_up_date']}")

            with col_b:
                st.subheader("🔑 Active Security Keys")
                if data["active_otps"]:
                    for otp in data["active_otps"]:
                        st.warning(f"Doctor Requested Access. Your OTP: **{otp['otp_code']}**")
                else:
                    st.success("No active data requests.")
                
                st.markdown("### 📜 Audit Logs")
                logs = requests.get(f"{BASE_URL}/audit_logs").json()
                for l in logs:
                    st.caption(f"{l['timestamp'][11:19]} - {l['event']}")

            st.markdown("---")
            st.subheader("💬 AI Health Assistant")
            user_input = st.text_input("Ask about your health or symptoms...")
            if user_input:
                triggers = ["chest pain", "breathing trouble", "heart attack", "unconscious"]
                if any(t in user_input.lower() for t in triggers):
                    st.error("🚨 EMERGENCY DETECTED: Based on your input, you may be having a severe medical event. Please call emergency services (108) immediately or visit the nearest ER.")
                elif "fever" in user_input.lower():
                    st.info("Assistant: Rest well, stay hydrated, and take paracetamol if prescribed. If fever persists above 102°F, contact your doctor.")
                else:
                    st.write("Assistant: I am a rule-based AI. I can answer simple queries. For emergencies, mention severe symptoms.")
