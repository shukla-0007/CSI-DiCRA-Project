from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import xgboost as xgb
import pandas as pd 
import os

# 1. INITIALIZE THE APP
app = FastAPI(title="DiCRA Compound Stress Index (CSI) API")

# 2. LOAD THE TRAINED MODEL
MODEL_PATH = "csi_model_v1.json"
model = xgb.XGBClassifier()

if os.path.exists(MODEL_PATH):
    model.load_model(MODEL_PATH)
else:
    # Fallback if running from the project root
    model.load_model("src/csi_model_v1.json")

# 3. DEFINE THE INPUT FORMAT (What the user sends us)
class ClimateInput(BaseModel):
    district_name: str
    lst: float # Temperature
    ssm: float # Soil Moisture
    ndvi: float # Vegetation index

# 4. THE PREDICTION ENDPOINT
@app.post("/predict_risk")
async def predict_risk(data: ClimateInput):
    try:
        # Create a single-row table for the model
        # We must use the EXACT column names used during training
        input_df = pd.DataFrame([{
            'LST': data.lst,
            'SSM': data.ssm,
            'NDVI': data.ndvi,
            'Heat_Anomaly': 1 if data.lst > 40 else 0, # Simple logic for the prototype
            'Drought_Anomaly': 1 if data.ssm < 0.1 else 0,
            'Compound_Stress': 1 if (data.lst > 40 and data.ssm < 0.1) else 0
        }])

        # Get probability (0.0 to 1.0)
        prob = model.predict_proba(input_df)[0][1]
        
        # Turn probability into a 1-5 Risk Tier (as per your proposal)
        risk_tier = int(prob * 4) + 1 # Maps 0.0-1.0 to 1-5

        return {
            "district": data.district_name,
            "risk_score": round(float(prob), 2),
            "risk_tier": risk_tier,
            "recommendation": "High Risk: Advise insurance uptake" if risk_tier >= 4 else "Low Risk: Normal monitoring"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "CSI Prediction Engine is Online"} 