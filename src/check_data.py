import pandas as pd

def diagnose():
    future_path = "data/raw/mp_CMIP6_Projections_2030.csv"
    df = pd.read_csv(future_path)
    
    print("--- FIRST 5 ROWS OF PROJECTION FILE ---")
    print(df.head())
    print("\n--- COLUMN NULL COUNTS ---")
    print(df.isnull().sum())
    print("\n--- TOTAL ROWS ---")
    print(len(df))

if __name__ == "__main__":
    diagnose() 
    
    