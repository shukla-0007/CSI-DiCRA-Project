import streamlit as st
import pandas as pd
import xgboost as xgb
import os

# 1. PAGE SETUP
st.set_page_config(page_title="DiCRA Climate Risk Dashboard", page_icon="🌍", layout="wide")

# 2. LOAD THE MODEL (Cached so it's lightning fast for recruiters)
@st.cache_resource
def load_model():
    model = xgb.XGBClassifier()
    # Check if running locally or in the cloud
    if os.path.exists("src/csi_model_v2.json"):
        model.load_model("src/csi_model_v2.json")
    elif os.path.exists("csi_model_v2.json"):
        model.load_model("csi_model_v2.json")
    return model

model = load_model()

# 3. HEADER
st.title("🌾 PMFBY Compound Stress Index (CSI) Tracker")
st.markdown("**Early Warning System for Agricultural Insurance** | Built on DiCRA & CMIP6")
st.divider()

# 4. SIDEBAR
with st.sidebar:
    st.header("⚙️ Simulation Parameters")
    district = st.selectbox("Select District", ["Bhopal", "Indore", "Vidarbha", "Agar Malwa", "Khandwa", "Dhar"])
    month = st.slider("Select Month", min_value=1, max_value=12, value=8, help="8 & 9 are Kharif Critical (Soybean). 1 & 2 are Rabi Critical.")
    lst = st.slider("Max Temperature (°C)", min_value=20.0, max_value=50.0, value=44.0, step=0.5)
    ssm = st.slider("Root-Zone Soil Moisture", min_value=0.01, max_value=0.50, value=0.05, step=0.01)
    st.markdown("---")
    analyze_button = st.button("🚀 Run Risk Analysis", use_container_width=True)

# 5. MAIN DASHBOARD
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Live District Analytics")
    st.write("Adjust the sliders on the left to simulate climate shocks and calculate parametric insurance triggers.")
    
    if analyze_button:
        with st.spinner("Calculating Spatiotemporal Risk..."):
            # Prepare data exactly how the model was trained
            kharif = 1 if month in [8, 9] else 0
            rabi = 1 if month in [1, 2] else 0
            non_critical = 1 if month not in [1, 2, 8, 9] else 0
            heat_anomaly = 1 if lst >= 42.0 else 0
            drought_anomaly = 1 if ssm <= 0.08 else 0

            input_df = pd.DataFrame([{
                'LST': lst, 'SSM': ssm, 
                'Heat_Anomaly': heat_anomaly, 'Drought_Anomaly': drought_anomaly,
                'Crop_Window_Kharif_Critical': kharif, 'Crop_Window_Rabi_Critical': rabi, 'Crop_Window_Non_Critical': non_critical
            }])

            # Make prediction
            prob = model.predict_proba(input_df)[0][1]
            
            # Actuarial Risk Tiers
            if prob < 0.20: risk_tier = 1
            elif prob < 0.40: risk_tier = 2
            elif prob < 0.60: risk_tier = 3
            elif prob < 0.80: risk_tier = 4
            else: risk_tier = 5

            # --- DISPLAY RESULTS ---
            st.markdown("### Model Output")
            m1, m2, m3 = st.columns(3)
            m1.metric(label="Target District", value=district)
            m2.metric(label="Actuarial Risk Tier", value=f"Tier {risk_tier} / 5")
            m3.metric(label="Probability of Crop Failure", value=f"{prob * 100:.1f}%")
            
            st.progress(float(prob))
            
            if risk_tier >= 4:
                st.error("🚨 **URGENT: Parametric Payout Triggered**")
                st.markdown("**Action Required:** Activate Payout Protocols. Alert KVK Agronomists.")
            elif risk_tier == 3:
                st.warning("⚠️ **Elevated Risk:** Close monitoring advised.")
            else:
                st.success("✅ **Safe:** Normal Monitoring")

with col2:
    st.subheader("Phenology Context")
    st.info("""
    **How the CSI Model Works:**
    It measures the *joint probability* of extreme heat AND drought occurring simultaneously during a critical crop growth window.
    * **Kharif Window:** Aug - Sept
    * **Rabi Window:** Jan - Feb
    """)  
    
show_future = st.checkbox("🔮 Show 2030 CMIP6 Projection") 