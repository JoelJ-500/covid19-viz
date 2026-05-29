import pandas as pd
import numpy as np

def load_and_clean_data(file_path):
    # Load CSV and parse dates
    print("--- Loading and Inspecting Data ---")
    df = pd.read_csv(file_path, parse_dates=['date'])
    print("\nHead of the data:")
    print(df.head())
    print("\nData Info:")
    print(df.info())

    # Handle missing values
    # new_vaccinations often has NaNs before rollout began, so fill with 0
    df['new_vaccinations'] = df['new_vaccinations'].fillna(0)
    # cases_per_million and vaccinations_per_hundred can be filled with 0 if missing
    df['cases_per_million'] = df['cases_per_million'].fillna(0)
    df['vaccinations_per_hundred'] = df['vaccinations_per_hundred'].fillna(0)

    # Convert count columns to float to handle float results from quantile calculations
    for col in ['new_cases', 'new_deaths']:
        df[col] = df[col].astype(float)

    # Handle mild outliers
    # Spikes in new_cases or new_deaths can sometimes be data entry errors.
    # We will cap values at the 99th percentile for each country to mitigate extreme spikes.
    for country in df['country'].unique():
        country_mask = df['country'] == country
        for col in ['new_cases', 'new_deaths']:
            q99 = df.loc[country_mask, col].quantile(0.99)
            df.loc[country_mask & (df[col] > q99), col] = q99
    
    print("\nMissing values handled and outliers capped at 99th percentile.")

    # Rolling means (7-day window) - compute per country
    df = df.sort_values(['country', 'date'])
    df['rolling_cases'] = df.groupby('country')['new_cases'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    df['rolling_deaths'] = df.groupby('country')['new_deaths'].transform(lambda x: x.rolling(window=7, min_periods=1).mean())
    
    # Monthly aggregates
    df['month'] = df['date'].dt.to_period('M')
    monthly_df = df.groupby(['country', 'month']).agg({
        'new_cases': 'sum',
        'new_deaths': 'sum',
        'new_vaccinations': 'sum'
    }).reset_index()

    # Save cleaned data and monthly aggregates to CSV
    df.to_csv("COVID_Cleaned.csv", index=False)
    monthly_df.to_csv("COVID_Monthly_Aggregates.csv", index=False)
    print("\nCleaned data saved to 'COVID_Cleaned.csv'")
    print("Monthly aggregates saved to 'COVID_Monthly_Aggregates.csv'")
    
    return df, monthly_df

if __name__ == "__main__":
    csv_file = "COVID_Country_Sample.csv"
    df, monthly_df = load_and_clean_data(csv_file)
    print("\nProcessed Data Sample:")
    print(df.head())
    print("\nMonthly Aggregate Sample:")
    print(monthly_df.head())
