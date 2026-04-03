import pandas as pd
import requests

def fetch_cmip6_projections(district_name, scenario="ssp245"):
    """
    Simulates fetching CMIP6 (RCP 4.5/8.5) data for a specific MP district.
    In production, this hits the World Bank CCKP or Copernicus API.
    """
    # Base URL for World Bank Climate API (example structure)
    # We will simulate the data structure for the 2026-2040 window
    years = list(range(2026, 2041))
    
    # Logic: Projected Tmax usually shows a +1.2 to +2.5 degree increase 
    # compared to your 1990-2024 baseline.
    projection_data = {
        "year": years,
        "district": [district_name] * len(years),
        "projected_tmax_anomaly": [1.5, 1.8, 2.1, 1.2, 3.0, 2.5, 1.9, 2.2, 2.8, 3.1, 1.4, 2.0, 2.6, 2.9, 3.2],
        "projected_precip_deficit": [0.85, 0.90, 0.70, 1.10, 0.60, 0.75, 0.88, 0.82, 0.55, 0.50, 0.95, 0.80, 0.70, 0.65, 0.50]
    }
    
    return pd.DataFrame(projection_data) 

# Test call
# df = fetch_cmip6_projections("Betul") 
# print(df.head()) 