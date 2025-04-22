import pandas as pd
import numpy as np
from scripts.utils import load_data, ensure_directory

def create_directories():
    os.makedirs("data/raw", exist_ok=True)
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("results/figures", exist_ok=True)
    os.makedirs("results/tables", exist_ok=True)

def load_india_debt_data():
    print("Loading India's debt data from CSV file...")
    
    try:
        df = load_data("notebooks/India.csv")
        raw_df = df.copy()

        ensure_directory("data/raw")
        raw_df.to_csv("data/raw/india_debt_statistics_raw.csv", index=False)
        print("Raw data saved to data/raw/india_debt_statistics_raw.csv")
        
        return raw_df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def main():
    create_directories()
    raw_df = load_india_debt_data()
    
    if raw_df is not None:
        print("Data acquisition completed successfully")
    else:
        print("Data acquisition failed")
    
if __name__ == "__main__":
    main()