import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scripts.utils import ensure_directory
import warnings

def load_processed_data():
    try:
        processed_df = pd.read_csv("data/processed/india_debt_processed.csv")
        long_df = pd.read_csv("data/processed/india_debt_long.csv")
        return processed_df, long_df
    except Exception as e:
        print(f"Error loading processed data: {e}")
        raise

def load_analysis_results():
    results = {}
    
    result_files = {
        'debt_by_type': 'results/tables/debt_by_type.csv',
        'debt_by_debtor': 'results/tables/debt_by_debtor.csv',
        'debt_flows': 'results/tables/debt_flows.csv',
        'debt_gdp_ratio': 'results/tables/debt_gdp_ratio.csv',
        'growth_rates': 'results/tables/growth_rates.csv'
    }
    
    for key, file_path in result_files.items():
        if os.path.exists(file_path):
            try:
                df = pd.read_csv(file_path)
                if not df.empty:
                    results[key] = df
                else:
                    print(f"Warning: {file_path} is empty")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
    
    return results

def create_trend_visualizations(df, long_df, results):
    ensure_directory("results/figures")

    if 'debt_by_type' in results and not results['debt_by_type'].empty:
        debt_by_type = results['debt_by_type']

        if 'Unnamed: 0' in debt_by_type.columns:
            debt_by_type = debt_by_type.rename(columns={'Unnamed: 0': 'Year'})
            years = debt_by_type['Year'].tolist()
        elif 'Year' in debt_by_type.columns:
            years = debt_by_type['Year'].tolist()
        else:
            years = debt_by_type.index.tolist()
            debt_by_type['Year'] = years

        if len(years) > 0 and all(isinstance(y, (int, float)) for y in years) and min(years) < 1900:
            print("Warning: Using index values instead of actual years for trend visualization")
            actual_years = list(range(2013, 2013 + len(years)))
            years = actual_years[:len(years)]
            debt_by_type['Year'] = years

        plt.figure(figsize=(12, 8))

        if 'Total External debt stocks' in debt_by_type.columns:
            plt.plot(years, debt_by_type['Total External debt stocks'], 'o-', linewidth=2, label='Total External Debt')

        if 'Long-term external debt' in debt_by_type.columns:
            plt.plot(years, debt_by_type['Long-term external debt'], 's-', linewidth=2, label='Long-term External Debt')

        if 'Short-term external debt' in debt_by_type.columns:
            plt.plot(years, debt_by_type['Short-term external debt'], '^-', linewidth=2, label='Short-term External Debt')
        
        plt.xlabel('Year')
        plt.ylabel('USD Millions')
        plt.title('India External Debt Trends (2013-2023)')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig('results/figures/india_debt_trends.png', dpi=300)

        components = [col for col in debt_by_type.columns if col not in ['Year', 'Unnamed: 0'] and not col.endswith('(%)')]
        
        if len(components) > 1:
            debt_components = pd.DataFrame({'Year': years})
            
            for component in components:
                if component in debt_by_type.columns:
                    debt_components[component] = debt_by_type[component]
            
            debt_components_melt = pd.melt(debt_components, id_vars=['Year'], 
                                        value_vars=[c for c in components if c in debt_components.columns],
                                        var_name='Component', value_name='Amount')
            
            fig = px.area(debt_components_melt, x='Year', y='Amount', color='Component',
                        title='Composition of India\'s External Debt')
            fig.update_layout(yaxis_title='USD Millions', legend_title='Debt Component')
            fig.write_html('results/figures/debt_composition.html')

    if 'debt_by_debtor' in results and not results['debt_by_debtor'].empty:
        debt_by_debtor_df = results['debt_by_debtor'].copy()

        if 'Unnamed: 0' in debt_by_debtor_df.columns:
            debt_by_debtor_df = debt_by_debtor_df.rename(columns={'Unnamed: 0': 'Year'})
            years = debt_by_debtor_df['Year'].tolist()
        elif 'Year' in debt_by_debtor_df.columns:
            years = debt_by_debtor_df['Year'].tolist()
        else:
            years = debt_by_debtor_df.index.tolist()
            debt_by_debtor_df['Year'] = years

        if len(years) > 0 and all(isinstance(y, (int, float)) for y in years) and min(years) < 1900:
            print("Warning: Using index values instead of actual years for debtor visualization")
            actual_years = list(range(2013, 2013 + len(years)))
            years = actual_years[:len(years)]
            debt_by_debtor_df['Year'] = years

        debtor_columns = [col for col in debt_by_debtor_df.columns if col not in ['Year', 'Unnamed: 0'] and not col.endswith('(%)')]
        
        if debtor_columns and len(years) > 0:
            try:
                debt_by_debtor_melt = pd.melt(debt_by_debtor_df, id_vars=['Year'], 
                                            value_vars=debtor_columns,
                                            var_name='Debtor Type', value_name='Amount')
                
                fig = px.bar(debt_by_debtor_melt, x='Year', y='Amount', color='Debtor Type',
                            title='India\'s External Debt by Debtor Type', barmode='stack')
                fig.update_layout(yaxis_title='USD Millions')
                fig.write_html('results/figures/debt_by_debtor.html')
            except Exception as e:
                print(f"Error creating debtor visualization: {e}")
        else:
            print("Warning: Not enough data for debtor type visualization")

def create_flow_visualizations(df, results):
    os.makedirs("results/figures", exist_ok=True)

    if 'debt_flows' in results and not results['debt_flows'].empty:
        debt_flows_df = results['debt_flows'].copy()

        if 'Unnamed: 0' in debt_flows_df.columns:
            debt_flows_df = debt_flows_df.rename(columns={'Unnamed: 0': 'Year'})
            years = debt_flows_df['Year'].tolist()
        elif 'Year' in debt_flows_df.columns:
            years = debt_flows_df['Year'].tolist()
        else:
            years = debt_flows_df.index.tolist()
            debt_flows_df['Year'] = years

        if len(years) > 0 and all(isinstance(y, (int, float)) for y in years) and min(years) < 1900:
            print("Warning: Using index values instead of actual years for flow visualization")
            actual_years = list(range(2013, 2013 + len(years)))
            years = actual_years[:len(years)]
            debt_flows_df['Year'] = years

        if 'Debt Service' in debt_flows_df.columns and len(years) > 0:
            try:
                fig = make_subplots(specs=[[{"secondary_y": True}]])
                fig.add_trace(go.Bar(x=years, y=debt_flows_df['Debt Service'], name='Debt Service'), secondary_y=False)
                
                if 'Debt Service Ratio (%)' in debt_flows_df.columns:
                    fig.add_trace(go.Scatter(x=years, y=debt_flows_df['Debt Service Ratio (%)'], 
                                            mode='lines+markers', name='Debt Service Ratio (%)'), secondary_y=True)
                
                fig.update_layout(title='India\'s Debt Service (2013-2023)')
                fig.update_xaxes(title_text='Year')
                fig.update_yaxes(title_text='USD Millions', secondary_y=False)
                fig.update_yaxes(title_text='Ratio (%)', secondary_y=True)
                fig.write_html('results/figures/debt_flows.html')
            except Exception as e:
                print(f"Error creating flow visualization: {e}")
        else:
            print("Warning: Not enough data for flow visualization")

    if 'growth_rates' in results and not results['growth_rates'].empty:
        growth_rates_df = results['growth_rates']

        if 'Unnamed: 0' in growth_rates_df.columns:
            warnings.filterwarnings("ignore", category=pd.errors.SettingWithCopyWarning)
            growth_rates_df = growth_rates_df.rename(columns={'Unnamed: 0': 'Year'})
            years = growth_rates_df['Year'].tolist() if 'Year' in growth_rates_df.columns else growth_rates_df.index.tolist()
        elif 'Year' in growth_rates_df.columns:
            years = growth_rates_df['Year'].tolist()
        else:
            years = growth_rates_df.index.tolist()
            if all(isinstance(y, (int, float)) for y in years) and min(years) < 1900:
                print("Warning: Using index values instead of actual years for growth rates")

        total_debt_growth_col = [col for col in growth_rates_df.columns if 'Total External debt stocks' in col]
        
        if total_debt_growth_col and len(years) > 0:
            growth_col = total_debt_growth_col[0]
            growth_data = growth_rates_df.loc[:, growth_col].dropna()
            
            if len(growth_data) > 0:
                plt.figure(figsize=(10, 6))
                x_values = years[:len(growth_data)] if len(years) >= len(growth_data) else range(len(growth_data))
                plt.bar(x_values, growth_data)
                avg_growth = growth_data.mean()
                plt.axhline(y=avg_growth, color='r', linestyle='-', label=f'Avg. Growth: {avg_growth:.2f}%')
                plt.xlabel('Year')
                plt.ylabel('Annual Change (%)')
                plt.title('Annual Growth Rate of India\'s External Debt')
                plt.legend()
                plt.tight_layout()
                plt.savefig('results/figures/debt_growth_rate.png', dpi=300)
            else:
                print("Warning: No growth data available for visualization")

def create_ratio_visualizations(results):
    os.makedirs("results/figures", exist_ok=True)
    
    if 'debt_gdp_ratio' in results and not results['debt_gdp_ratio'].empty:
        debt_gdp = results['debt_gdp_ratio'].copy()
        
        if 'Year' in debt_gdp.columns and 'Debt to GDP Ratio (%)' in debt_gdp.columns:
            try:
                debt_gdp['Year'] = pd.to_numeric(debt_gdp['Year'], errors='coerce')
                debt_gdp = debt_gdp.dropna(subset=['Year', 'Debt to GDP Ratio (%)'])
                
                if not debt_gdp.empty:
                    plt.figure(figsize=(10, 6))
                    plt.plot(debt_gdp['Year'], debt_gdp['Debt to GDP Ratio (%)'], 'o-', linewidth=2)
                    plt.xlabel('Year')
                    plt.ylabel('Debt to GDP Ratio (%)')
                    plt.title('India\'s External Debt to GDP Ratio (2013-2023)')
                    plt.grid(True)
                    plt.tight_layout()
                    plt.savefig('results/figures/debt_gdp_ratio.png', dpi=300)
                else:
                    print("Warning: No valid data for GDP ratio visualization")
            except Exception as e:
                print(f"Error creating GDP ratio visualization: {e}")
    
    if 'debt_flows' in results and not results['debt_flows'].empty:
        debt_flows = results['debt_flows'].copy()

        years = None
        if 'Unnamed: 0' in debt_flows.columns:
            debt_flows = debt_flows.rename(columns={'Unnamed: 0': 'Year'})
            years = debt_flows['Year'].tolist()
        elif 'Year' in debt_flows.columns:
            years = debt_flows['Year'].tolist()
        else:
            years = debt_flows.index.tolist()
            debt_flows['Year'] = years

        if len(years) > 0 and all(isinstance(y, (int, float)) for y in years) and min(years) < 1900:
            print("Warning: Using index values instead of actual years for ratio visualization")
            actual_years = list(range(2013, 2013 + len(years)))
            years = actual_years[:len(years)]
            debt_flows['Year'] = years
        
        if 'Debt Service Ratio (%)' in debt_flows.columns and len(years) > 0:
            try:
                plt.figure(figsize=(10, 6))
                plt.plot(years, debt_flows['Debt Service Ratio (%)'], 'o-', linewidth=2)
                plt.xlabel('Year')
                plt.ylabel('Debt Service Ratio (%)')
                plt.title('India\'s Debt Service Ratio (2013-2023)')
                plt.grid(True)
                plt.tight_layout()
                plt.savefig('results/figures/debt_service_ratio.png', dpi=300)
            except Exception as e:
                print(f"Error creating debt service ratio visualization: {e}")
        else:
            print("Warning: No debt service ratio data available for visualization")

def create_correlation_matrix(processed_df, results):
    os.makedirs("results/figures", exist_ok=True)

    debt_components = pd.DataFrame()
    
    if 'debt_by_type' in results and not results['debt_by_type'].empty:
        debt_by_type = results['debt_by_type']
        value_cols = [col for col in debt_by_type.columns if not col.endswith('(%)') and col != 'Unnamed: 0']
        debt_components = debt_by_type[value_cols]
    
    if 'debt_by_debtor' in results and not results['debt_by_debtor'].empty:
        debt_by_debtor = results['debt_by_debtor']
        value_cols = [col for col in debt_by_debtor.columns if not col.endswith('(%)') and col != 'Unnamed: 0']
        if not debt_components.empty:
            for col in value_cols:
                if col not in debt_components.columns:
                    debt_components[col] = debt_by_debtor[col]
        else:
            debt_components = debt_by_debtor[value_cols]
    
    if 'debt_flows' in results and not results['debt_flows'].empty:
        debt_flows = results['debt_flows']
        value_cols = [col for col in debt_flows.columns if not col.endswith('(%)') and col != 'Unnamed: 0']
        if not debt_components.empty:
            for col in value_cols:
                if col not in debt_components.columns:
                    debt_components[col] = debt_flows[col]
        else:
            debt_components = debt_flows[value_cols]

    if not debt_components.empty and debt_components.shape[1] > 1:
        correlation = debt_components.corr()
        plt.figure(figsize=(12, 10))
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f', linewidths=.5)
        plt.title('Correlation Matrix of Debt Components')
        plt.tight_layout()
        plt.savefig('results/figures/debt_correlation.png', dpi=300)
    else:
        print("Warning: Not enough data for correlation matrix")

def main():
    processed_df, long_df = load_processed_data()
    analysis_results = load_analysis_results()
    
    create_trend_visualizations(processed_df, long_df, analysis_results)
    create_flow_visualizations(processed_df, analysis_results)
    create_ratio_visualizations(analysis_results)
    create_correlation_matrix(processed_df, analysis_results)
    
    print("Visualizations created successfully")

if __name__ == "__main__":
    main()