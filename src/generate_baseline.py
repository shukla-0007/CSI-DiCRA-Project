import pandas as pd
import os

def generate_real_baselines():
    file_path = "data/raw/mp_15yr_climate_backbone.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ File {file_path} not found!")
        return

    df = pd.read_csv(file_path)
    print(f"📖 Loaded data. Found columns: {list(df.columns)}")

    # MAPPING FOR DICRA/SATELLITE TERMS
    dist_col = 'District'
    tmax_col = 'LST'  # Mapping LST to Temperature
    sm_col = 'SSM'    # Mapping SSM to Soil Moisture

    print(f"🔍 Mapping: District='{dist_col}', Tmax='{tmax_col}', SoilMoisture='{sm_col}'")

    # Calculate 95th percentile LST and 5th percentile SSM per district
    baseline = df.groupby(dist_col).agg({
        tmax_col: lambda x: x.quantile(0.95),
        sm_col: lambda x: x.quantile(0.05)
    }).reset_index()
    
    baseline.columns = ['district', 'tmax_95th', 'sm_5th']
    
    os.makedirs("data", exist_ok=True)
    baseline.to_csv("data/district_baselines.csv", index=False)
    print(f"✅ Real Baselines generated for {len(baseline)} districts.")

if __name__ == "__main__":
    generate_real_baselines() 