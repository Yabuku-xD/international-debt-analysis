import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns

def ensure_directory(directory):
    os.makedirs(directory, exist_ok=True)

def setup_directories():
    directories = [
        "data/raw",
        "data/processed", 
        "results/figures", 
        "results/tables"
    ]
    for directory in directories:
        ensure_directory(directory)
    return True

def load_data(file_path, encodings=["latin1", "cp1252", "ISO-8859-1"]):
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

def save_dataframe(df, path, index=False):
    ensure_directory(os.path.dirname(path))
    df.to_csv(path, index=index)
    print(f"Data saved to {path}")

def create_long_format(df):
    long_format = pd.DataFrame()
    
    for column in df.columns:
        if column != 'Year':
            temp_df = pd.DataFrame({
                'Year': df['Year'],
                'Indicator': column,
                'Value': df[column]
            })
            long_format = pd.concat([long_format, temp_df])
    
    return long_format

def get_year_columns(df):
    return [col for col in df.columns if str(col).isdigit()]

def set_visualization_style():
    plt.style.use('ggplot')
    sns.set_palette("viridis")
    return True