import pandas as pd
import xgboost as xgb
import os

class ClimateForecaster:
    def __init__(self, model_path="src/mp_production_model_v1.json"):
        self.model = xgb.XGBClassifier()
        if os.path.exists(model_path):
            self.model.load_model(model_path)
        else:
            self.model.load_model("mp_production_model_v1.json")

    def process_cmip6(self, path):
        df = pd.read_csv(path)
        # Convert Kelvin to Celsius and Rain to Daily Total
        df['LST'] = df['tasmax'] - 273.15
        df['SSM'] = 0.15 # Baseline assumption as CMIP6 doesn't provide root-zone SM directly
        
        df['Date'] = pd.to_datetime(df['Date'])
        df['Month'] = df['Date'].dt.month
        
        # Features needed for model
        df['Heat_Anomaly'] = (df['LST'] > 42.0).astype(int)
        df['Drought_Anomaly'] = (df['SSM'] < 0.1).astype(int)
        df['Is_Kharif_Critical'] = df['Month'].isin([8, 9]).astype(int)
        df['Is_Rabi_Critical'] = df['Month'].isin([1, 2]).astype(int)
        df['CSI_Event'] = (df['Heat_Anomaly'] & df['Drought_Anomaly'] & (df['Is_Kharif_Critical'] | df['Is_Rabi_Critical']))

        features = ['LST', 'SSM', 'Heat_Anomaly', 'Drought_Anomaly', 'Is_Kharif_Critical', 'Is_Rabi_Critical', 'CSI_Event']
        
        # Predict Probabilities
        df['Risk_Probability'] = self.model.predict_proba(df[features])[:, 1]
        df['Risk_Tier'] = (df['Risk_Probability'] * 4 + 1).astype(int)
        
        return df[['Date', 'district_name', 'LST', 'Risk_Probability', 'Risk_Tier']]

# Usage for your tests:
# forecaster = ClimateForecaster()
# future_results = forecaster.process_cmip6("../data/raw/MP_CMIP6_Projections_2030.csv") 