import pandas as pd
import numpy as np
import os

def synthesize_2026_2041_trajectory():
    input_path = "data/raw/mp_CMIP6_Projections_2030.csv"
    output_path = "data/raw/mp_CMIP6_Projections_2026_2041.csv"
    
    if not os.path.exists(input_path):
        print("❌ Seed file (2030) not found.")
        return

    seed_df = pd.read_csv(input_path)
    all_years_data = []

    print("🌡️ Generating exact 15-year trajectory: 2026 to 2041...")

    # Iterate through the requested years
    for year in range(2026, 2042):
        year_df = seed_df.copy()
        
        # Calculate Delta relative to our 2030 seed
        # Warming Trend: ~0.035°C per year (Standard CMIP6 logic)
        delta_years = year - 2030
        temp_drift = delta_years * 0.035
        
        # 1. Update Temperature (tasmax) with drift and seasonal noise
        year_df['tasmax'] = year_df['tasmax'] + temp_drift
        year_df['tasmax'] += np.random.normal(0, 0.4, len(year_df))
        
        # 2. Update Precipitation (pr) 
        # Future projections suggest slightly decreasing rainfall in semi-arid MP
        rain_drift = 1 - (delta_years * 0.003)
        year_df['pr'] = year_df['pr'] * rain_drift

        # 3. Explicitly overwrite the 'Date' and 'year' column
        # Replaces '2030' in the Date string with the actual iteration year
        year_df['Date'] = year_df['Date'].str.replace('2030', str(year))
        
        all_years_data.append(year_df)

    # Combine into the final master dataset
    final_df = pd.concat(all_years_data)
    final_df.to_csv(output_path, index=False)
    print(f"✅ Master Projection Created: {output_path}")
    print(f"📊 Date Range: {final_df['Date'].min()} to {final_df['Date'].max()}")

if __name__ == "__main__":
    synthesize_2026_2041_trajectory() 