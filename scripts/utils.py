import pandas as pd
import numpy as np
import os

def load_data(file_path="notebooks/India.csv", encodings=["latin1", "cp1252", "ISO-8859-1"]):
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            print(f"CSV file loaded successfully with {encoding} encoding")
            return df
        except Exception as e:
            print(f"Error with {encoding} encoding: {e}")
            continue
    
    raise ValueError(f"Failed to load {file_path} with any of the provided encodings")

def extract_value(df_filtered, year):
    if not df_filtered.empty and year in df_filtered.columns:
        value = df_filtered[year].iloc[0]
        if isinstance(value, str):
            return float(value.replace(',', ''))
        return float(value)
    return 0

def save_processed_data(processed_df, long_format, base_dir="data/processed"):
    os.makedirs(base_dir, exist_ok=True)
    processed_df.to_csv(f"{base_dir}/india_debt_processed.csv", index=False)
    long_format.to_csv(f"{base_dir}/india_debt_long.csv", index=False)
    print(f"Data saved to {base_dir} directory")

def create_long_format(processed_df):
    long_format = pd.DataFrame()
    for metric in processed_df.columns:
        if metric != 'Year':
            temp_df = pd.DataFrame({
                'Year': processed_df['Year'],
                'Indicator': metric,
                'Value': processed_df[metric]
            })
            long_format = pd.concat([long_format, temp_df])
    return long_format

def ensure_directory(directory):
    os.makedirs(directory, exist_ok=True)