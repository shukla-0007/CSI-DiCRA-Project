import streamlit as st
import requests
import pandas as pd

# 1. PAGE SETUP (Make it look professional)
st.set_page_config(
    page_title="DiCRA Climate Risk Dashboard",
    page_icon="🌍",
    layout="wide"
)

# 2. CUSTOM CSS (To make the metrics look like a real SaaS product)
st.markdown("""
    <style>
    .main {background-color: #f8f9fa;}
    h1 {color: #004C99;}
    .stAlert {font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# 3. HEADER
st.title("🌾 PMFBY Compound Stress Index (CSI) Tracker")
st.markdown("**Early Warning System for Agricultural Insurance** | Built on DiCRA & CMIP6")
st.divider()

# 4. SIDEBAR (User Inputs)
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    
    # We list a few MP Districts
    district = st.selectbox("Select District", 
                            ["Bhopal", "Indore", "Vidarbha", "Agar Malwa", "Khandwa", "Dhar"])
    
    month = st.slider("Select Month", min_value=1, max_value=12, value=8, 
                      help="8 & 9 are Kharif Critical (Soybean). 1 & 2 are Rabi Critical (Wheat).")
    
    lst = st.slider("Max Temperature (°C)", min_value=20.0, max_value=50.0, value=44.0, step=0.5)
    ssm = st.slider("Root-Zone Soil Moisture", min_value=0.01, max_value=0.50, value=0.05, step=0.01)
    
    st.markdown("---")
    analyze_button = st.button("🚀 Run Risk Analysis", use_container_width=True)

# 5. MAIN DASHBOARD AREA
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live District Analytics")
    st.write("Adjust the sliders on the left to simulate climate shocks and calculate parametric insurance triggers.")
    
    # When the user clicks the button, we ping your FastAPI server!
    if analyze_button:
        with st.spinner("Querying Machine Learning Model..."):
            
            # The URL of your FastAPI server
            API_URL = "http://127.0.0.1:8000/predict_risk"
            
            payload = {
                "district_name": district,
                "month": month,
                "lst": lst,
                "ssm": ssm
            }
            
            try:
                # Send data to your backend
                response = requests.post(API_URL, json=payload)
                data = response.json()
                
                # --- DISPLAY RESULTS ---
                st.markdown("### Model Output")
                
                # Create beautiful metric cards
                m1, m2, m3 = st.columns(3)
                m1.metric(label="Target District", value=data["district"])
                m2.metric(label="Actuarial Risk Tier", value=f"Tier {data['risk_tier']} / 5")
                m3.metric(label="Probability of Crop Failure", value=f"{data['risk_score'] * 100:.1f}%")
                
                # Progress Bar for Visual Impact
                st.progress(data['risk_score'])
                
                # Dynamic Alert Box based on Risk Tier
                if data['risk_tier'] >= 4:
                    st.error(f"🚨 {data['recommendation']}")
                    st.markdown("""
                        **Action Required:**
                        * Activate Parametric Payout Protocols.
                        * Alert KVK Agronomists for targeted interventions.
                    """)
                elif data['risk_tier'] == 3:
                    st.warning(f"⚠️ {data['recommendation']}")
                else:
                    st.success(f"✅ {data['recommendation']}")
                    
            except Exception as e:
                st.error(f"Backend API Error: Ensure your FastAPI server is running! ({e})")

with col2:
    st.subheader("Phenology Context")
    st.info("""
    **How the CSI Model Works:**
    It does not just measure heat. It measures the *joint probability* of extreme heat AND drought occurring simultaneously during a critical crop growth window.
    
    * **Kharif Window:** Aug - Sept
    * **Rabi Window:** Jan - Feb
    """) 