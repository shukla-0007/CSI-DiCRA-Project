import pandas as pd
import requests
import os
import time

# 1. Load the CORRECT CSV file (Not the .json)
coords_path = "/Users/sigma-7/Documents/CSI-DiCRA-Project/CSI-DiCRA-Project/data/mp_district_coordinates.csv"
if not os.path.exists(coords_path):
    print(f"❌ ERROR: {coords_path} not found. Run Step 1 first!")
    exit()

coords_df = pd.read_csv(coords_path)

# 2. Define the NASA POWER API Template
BASE_URL = "https://power.larc.nasa.gov/api/temporal/daily/point"

def fetch_nasa_data(lat, lon, dist_name):
    params = {
        "start": "20100101",
        "end": "20241231",
        "latitude": lat,
        "longitude": lon,
        "community": "ag",
        "parameters": "T2M_MAX,GWETROOT",
        "format": "JSON"
    }
    
    try:
        print(f"📡 Requesting 15-year history for {dist_name}...")
        response = requests.get(BASE_URL, params=params, timeout=30)
        
        if response.status_code == 200:
            data = response.json()['properties']['parameter']
            # Convert NASA's nested JSON to a clean Table
            df = pd.DataFrame(data)
            df['District'] = dist_name
            df.index.name = 'Date'
            return df.reset_index()
        else:
            print(f"⚠️ API Error {response.status_code} for {dist_name}")
            return None
    except Exception as e:
        print(f"❌ Connection failed for {dist_name}: {e}")
        return None

# 3. THE MASTER HARVESTER
all_data = []

for idx, row in coords_df.iterrows():
    dist_data = fetch_nasa_data(row['lat'], row['lon'], row['district_name'])
    if dist_data is not None:
        all_data.append(dist_data)
    
    # NASA POWER allows limited requests per minute, keep the sleep
    time.sleep(1)

# 4. CONSOLIDATE AND SAVE
if all_data:
    final_df = pd.concat(all_data, ignore_index=True)
    
    # Rename columns to match your model's expected names
    # T2M_MAX -> LST | GWETROOT -> SSM
    final_df = final_df.rename(columns={'T2M_MAX': 'LST', 'GWETROOT': 'SSM'})
    
    os.makedirs("../data/raw", exist_ok=True)
    final_df.to_csv("../data/raw/mp_15yr_climate_backbone.csv", index=False)
    print("\n✅ SUCCESS: 15-year backbone saved to data/raw/mp_15yr_climate_backbone.csv")
else:
    print("❌ No data harvested.") 
    
