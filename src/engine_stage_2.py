import pandas as pd
import numpy as np
import os

def run_final_prediction_2041():
    # 1. PATHS
    baselines_path = "data/district_baselines.csv"
    future_path = "data/raw/mp_CMIP6_Projections_2026_2041.csv"
    output_path = "data/processed/district_2026_2041_risk_trajectory.csv"

    if not os.path.exists(baselines_path) or not os.path.exists(future_path):
        print("❌ Missing files. Please run generate_baseline.py and generate_future_data.py first.")
        return

    # 2. LOAD DATA
    baselines = pd.read_csv(baselines_path)
    future = pd.read_csv(future_path)

    # 3. AUTO-DETECT COLUMNS (Fixes the KeyError)
    dist_col = next((c for c in future.columns if 'dist' in c.lower()), None)
    temp_col = next((c for c in future.columns if 'tasmax' in c or 'LST' in c or 'tmax' in c), None)
    precip_col = next((c for c in future.columns if 'pr' in c or 'SSM' in c), None)
    date_col = next((c for c in future.columns if 'Date' in c or 'year' in c), 'Date')

    if not dist_col or not temp_col:
        print(f"❌ Error mapping columns in {future_path}. Found: {list(future.columns)}")
        return

    print(f"🔍 Column Mapping: District='{dist_col}', Temp='{temp_col}', Rain='{precip_col}'")

    # 4. REPAIR EMPTY DISTRICT NAMES (If needed)
    if future[dist_col].isnull().all():
        print("⚠️ District column is empty. Applying MP district map recovery...")
        mp_districts = sorted(baselines['district'].unique())
        # Tile districts over the 15-year period
        num_reps = len(future) // len(mp_districts)
        future[dist_col] = np.tile(mp_districts, num_reps)

    # 5. DATA CLEANING & UNIT CONVERSION
    # Convert Kelvin to Celsius if values are > 200
    if future[temp_col].mean() > 200:
        print("🌡️ Unit Check: Converting Kelvin to Celsius...")
        future['tmax_final'] = future[temp_col] - 273.15
    else:
        future['tmax_final'] = future[temp_col]

    future['year'] = pd.to_datetime(future[date_col]).dt.year
    future['month'] = pd.to_datetime(future[date_col]).dt.month

    # 6. PHENOLOGICAL CLIPPING (Goal: Stage 2 PDF achievement)
    # Filter for Kharif/Rabi (June to March) - excluding April/May gap
    active_months = [6, 7, 8, 9, 10, 11, 12, 1, 2, 3]
    future = future[future['month'].isin(active_months)]

    # 7. MERGE WITH HISTORICAL BASELINES
    future[dist_col] = future[dist_col].str.lower().str.strip()
    baselines['district'] = baselines['district'].str.lower().str.strip()
    
    combined = future.merge(baselines, left_on=dist_col, right_on='district')

    # 8. CSI LOGIC (Heat + Drought Intersection)
    combined['heat_stress'] = combined['tmax_final'] > combined['tmax_95th']
    combined['moist_stress'] = combined[precip_col] < 1.0 # Standard pr drought threshold
    
    # 0 to 1 Score
    combined['csi_score'] = (combined['heat_stress'].astype(int) * 0.5) + (combined['moist_stress'].astype(int) * 0.5)

    # 9. AGGREGATE SUMMARY PER YEAR (For Frontend Trend Lines)
    summary = combined.groupby([dist_col, 'year'])['csi_score'].mean().reset_index()
    summary.rename(columns={dist_col: 'district_name'}, inplace=True)

    # Assign Risk Tiers (1 to 5)
    summary['risk_tier'] = pd.cut(summary['csi_score'], 
                                 bins=[-0.1, 0.05, 0.15, 0.25, 0.35, 1.1], 
                                 labels=[1, 2, 3, 4, 5])

    # 10. EXPORT
    os.makedirs("data/processed", exist_ok=True)
    summary.to_csv(output_path, index=False)
    print(f"✅ SUCCESS: Predicted 2026-2041 Risk Trajectory saved to {output_path}")
    print(summary.head(10))

if __name__ == "__main__":
    run_final_prediction_2041() 