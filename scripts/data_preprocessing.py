import pandas as pd
import numpy as np
from scripts.utils import load_data, extract_value, save_processed_data, create_long_format, ensure_directory

def load_cleaned_data():
    return load_data("notebooks/India.csv")

def process_data(df):
    print("Processing data...")
    indicator_col = df.columns[0]
    print(f"Indicator column: {indicator_col}")
    print("Available columns:", df.columns.tolist())

    indicators = {
        "principal_repayments": "Principal repayments (long-term)",
        "interest_payments": "Interest payments (long-term)",
        "total_debt": "Total External debt stocks",
        "short_term_debt": "Short-term external debt",
        "public_sector": "Public sector"
    }

    indicator_dfs = {}
    for key, indicator_name in indicators.items():
        indicator_dfs[key] = df[df[indicator_col] == indicator_name]
    
    years = [col for col in df.columns[1:] if str(col).isdigit()]
    print(f"Years found: {years}")

    processed_data = {"Year": years}
    metrics = ["Total External debt stocks", "debt_service", "debt_service_ratio", 
            "short_term_ratio", "public_debt_ratio"]
    
    for metric in metrics:
        processed_data[metric] = []

    for year in years:
        try:
            principal_value = extract_value(indicator_dfs["principal_repayments"], year)
            interest_value = extract_value(indicator_dfs["interest_payments"], year)
            total_debt_value = extract_value(indicator_dfs["total_debt"], year)
            short_term_value = extract_value(indicator_dfs["short_term_debt"], year)
            public_sector_value = extract_value(indicator_dfs["public_sector"], year)

            debt_service = principal_value + interest_value
            
            if total_debt_value > 0:
                debt_service_ratio = (debt_service / total_debt_value) * 100
                short_term_ratio = (short_term_value / total_debt_value) * 100
                public_debt_ratio = (public_sector_value / total_debt_value) * 100
            else:
                debt_service_ratio = 0
                short_term_ratio = 0
                public_debt_ratio = 0

            processed_data["Total External debt stocks"].append(total_debt_value)
            processed_data["debt_service"].append(debt_service)
            processed_data["debt_service_ratio"].append(debt_service_ratio)
            processed_data["short_term_ratio"].append(short_term_ratio)
            processed_data["public_debt_ratio"].append(public_debt_ratio)
            
        except Exception as e:
            print(f"Error processing year {year}: {e}")

    processed_df = pd.DataFrame(processed_data)

    processed_df['annual_growth_rate'] = processed_df['Total External debt stocks'].pct_change() * 100

    long_format = create_long_format(processed_df)

    save_processed_data(processed_df, long_format)
    
    print("Data processing completed successfully")
    return processed_df, long_format

def main():
    df = load_cleaned_data()
    processed_df, long_format = process_data(df)
    print("Data preprocessing completed successfully")

if __name__ == "__main__":
    main()