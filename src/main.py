from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import pandas as pd
import os

app = FastAPI(title="DiCRA Compound Stress Index (CSI) API")

# LOAD THE NEW MASTER MODEL
MODEL_PATH = "csi_model_v2.json"
model = xgb.XGBClassifier()
if os.path.exists(MODEL_PATH):
    model.load_model(MODEL_PATH)
else:
    model.load_model("src/csi_model_v2.json")

class ClimateInput(BaseModel):
    district_name: str
    month: int       # Added Month for Crop Calendar!
    lst: float       # Temperature
    ssm: float       # Soil Moisture

@app.post("/predict_risk")
async def predict_risk(data: ClimateInput):
    try:
        # Determine Crop Window based on the month
        kharif = 1 if data.month in [8, 9] else 0
        rabi = 1 if data.month in [1, 2] else 0
        non_critical = 1 if data.month not in [1, 2, 8, 9] else 0
        
        # Calculate dynamic anomalies (In production, these come from historical DB)
        # For the API, we use typical MP extremes: > 42C is heat, < 0.08 is drought
        heat_anomaly = 1 if data.lst >= 42.0 else 0
        drought_anomaly = 1 if data.ssm <= 0.08 else 0

        input_df = pd.DataFrame([{
            'LST': data.lst,
            'SSM': data.ssm,
            'Heat_Anomaly': heat_anomaly,
            'Drought_Anomaly': drought_anomaly,
            'Crop_Window_Kharif_Critical': kharif,
            'Crop_Window_Rabi_Critical': rabi,
            'Crop_Window_Non_Critical': non_critical
        }])

        # Get probability
        prob = model.predict_proba(input_df)[0][1]
        
        # Actuarial Risk Tiers (1 to 5)
        if prob < 0.20: risk_tier = 1
        elif prob < 0.40: risk_tier = 2
        elif prob < 0.60: risk_tier = 3
        elif prob < 0.80: risk_tier = 4
        else: risk_tier = 5

        return {
            "district": data.district_name,
            "month": data.month,
            "risk_score": round(float(prob), 4),
            "risk_tier": risk_tier,
            "recommendation": "URGENT: Parametric Payout Triggered" if risk_tier == 5 else "Safe: Normal Monitoring"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 