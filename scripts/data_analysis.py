import pandas as pd
import numpy as np
import statsmodels.api as sm
from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from scripts.utils import ensure_directory

def load_processed_data():
    try:
        processed_df = pd.read_csv("data/processed/india_debt_processed.csv")
        long_df = pd.read_csv("data/processed/india_debt_long.csv")
        return processed_df, long_df
    except Exception as e:
        print(f"Error loading processed data: {e}")
        raise

def time_series_analysis(df):
    ensure_directory("results/tables")
    
    results = {}

    if 'Year' in df.columns:
        years = df['Year'].astype(int).tolist()
        debt_values = df['Total External debt stocks'].tolist()
    else:
        years = [int(col) for col in df.columns[1:] if col.isdigit()]
        total_debt_row = df[df.iloc[:, 0] == 'Total External debt stocks']
        debt_values = [total_debt_row[str(year)].iloc[0] for year in years]
    
    debt_series = pd.Series(debt_values, index=years)
    
    if len(years) > 6:
        decomposition = seasonal_decompose(debt_series, model='additive', period=3)
        trend = decomposition.trend
        seasonal = decomposition.seasonal
        residual = decomposition.resid
        
        results['decomposition'] = pd.DataFrame({
            'Year': trend.index,
            'Original': debt_series,
            'Trend': trend,
            'Seasonal': seasonal,
            'Residual': residual
        })

    debt_series_clean = debt_series.dropna()
    if len(debt_series_clean) > 1:
        adf_result = adfuller(debt_series_clean)
        results['stationarity'] = {
            'Test Statistic': adf_result[0],
            'p-value': adf_result[1],
            'Critical Values': adf_result[4]
        }
    else:
        print("Warning: Not enough data points for time series analysis")
        results['stationarity'] = {
            'Test Statistic': None,
            'p-value': None,
            'Critical Values': None
        }

    growth_rates = pd.DataFrame(index=years)
    growth_rates['Total External debt stocks_growth'] = debt_series.pct_change() * 100
    results['growth_rates'] = growth_rates

    gdp_estimates = {
        2013: 1.8568e6,
        2014: 2.0396e6,
        2015: 2.0964e6,
        2016: 2.2944e6,
        2017: 2.6527e6,
        2018: 2.7012e6,
        2019: 2.8704e6,
        2020: 2.6681e6,
        2021: 3.1760e6,
        2022: 3.3848e6,
        2023: 3.5342e6
    }

    debt_gdp_ratio = pd.DataFrame({
        'Year': years,
        'Debt (USD millions)': debt_values,
        'GDP (USD millions)': [gdp_estimates.get(year, 0) for year in years]
    })

    debt_gdp_ratio['Debt to GDP Ratio (%)'] = (debt_gdp_ratio['Debt (USD millions)'] / debt_gdp_ratio['GDP (USD millions)']) * 100
    
    results['debt_gdp_ratio'] = debt_gdp_ratio

    for key, result in results.items():
        if isinstance(result, pd.DataFrame):
            result.to_csv(f"results/tables/{key}.csv", index=False)
    
    with open("results/tables/summary_statistics.txt", "w") as f:
        for key, result in results.items():
            if not isinstance(result, pd.DataFrame):
                f.write(f"{key}:\n")
                f.write(str(result))
                f.write("\n\n")
    
    return results

def debt_composition_analysis(df, long_df):
    ensure_directory("results/tables")
    if 'Year' in df.columns:
        years = df['Year'].astype(int).tolist()
    else:
        years = [int(col) for col in df.columns[1:] if col.isdigit()]

    debt_by_type = pd.DataFrame(index=years)
    debt_by_debtor = pd.DataFrame(index=years)
    debt_flows = pd.DataFrame(index=years)

    for i, year in enumerate(years):
        total_debt_value = df['Total External debt stocks'].iloc[i]
        debt_by_type.at[year, 'Total External debt stocks'] = total_debt_value

        short_term_ratio = df['short_term_ratio'].iloc[i]
        short_term_debt = (short_term_ratio * total_debt_value) / 100
        debt_by_type.at[year, 'Short-term external debt'] = short_term_debt
        debt_by_type.at[year, 'Short-term external debt (%)'] = short_term_ratio

        public_debt_ratio = df['public_debt_ratio'].iloc[i]
        public_debt = (public_debt_ratio * total_debt_value) / 100
        debt_by_type.at[year, 'Public sector'] = public_debt
        debt_by_type.at[year, 'Public sector (%)'] = public_debt_ratio

        debt_flows.at[year, 'Debt Service'] = df['debt_service'].iloc[i]
        debt_flows.at[year, 'Debt Service Ratio (%)'] = df['debt_service_ratio'].iloc[i]

        debt_by_debtor.at[year, 'Public sector'] = public_debt
        debt_by_debtor.at[year, 'Public sector (%)'] = public_debt_ratio

        private_sector = total_debt_value - public_debt
        debt_by_debtor.at[year, 'Private sector not guaranteed'] = private_sector
        debt_by_debtor.at[year, 'Private sector not guaranteed (%)'] = 100 - public_debt_ratio

    debt_by_type.reset_index(names='Year').to_csv("results/tables/debt_by_type.csv", index=False)
    debt_by_debtor.reset_index(names='Year').to_csv("results/tables/debt_by_debtor.csv", index=False)
    debt_flows.reset_index(names='Year').to_csv("results/tables/debt_flows.csv", index=False)
    
    return {
        'debt_by_type': debt_by_type,
        'debt_by_debtor': debt_by_debtor,
        'debt_flows': debt_flows
    }

def main():
    processed_df, long_df = load_processed_data()
    time_series_analysis(processed_df)
    debt_composition_analysis(processed_df, long_df)
    print("Data analysis completed successfully")

if __name__ == "__main__":
    main()