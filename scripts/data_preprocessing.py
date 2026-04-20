import pandas as pd
import numpy as np

# Load raw datasets
def load_world_bank(path, value_name):
    df = pd.read_csv(path, skiprows=4)
    df = df[df['Country Name'] == 'India']
    df = df.drop(columns=['Country Name', 'Country Code', 'Indicator Name', 'Indicator Code', 'Unnamed: 70'], errors='ignore')
    df = df.melt(var_name='Year', value_name=value_name)
    df['Year'] = df['Year'].astype(int)
    return df

gdp = load_world_bank("data/raw/API_GDP.csv", "GDP")
inflation = load_world_bank("data/raw/API_INFLATION.csv", "Inflation")
unemployment = load_world_bank("data/raw/unemployeement_india.csv", "Unemployment")
interest_rate = load_world_bank("data/raw/interest_rate.csv", "Interest_Rate")

# Population data
pop = pd.read_csv("data/raw/indianPopulation.csv")
pop['Year'] = pop['Year'].astype(int)
pop['Population'] = pop['Population'].str.replace(',', '').astype(float)
population = pop[['Year', 'Population']]

# Budget data (Revenue, Expenditure)
budget = pd.read_csv("data/raw/budget_glance.csv")
# Mapping years: 2021-2022 Actuals -> 2021, 2022-2023 RE -> 2022, 2023-2024 BE -> 2023
rev = budget[budget['SI. No.        Parameters'].str.contains('Revenue Receipts', na=False)].iloc[0]
exp = budget[budget['SI. No.        Parameters'].str.contains('Total Expenditure', na=False)].iloc[0]

budget_data = pd.DataFrame({
    'Year': [2021, 2022, 2023],
    'Revenue': [float(rev['2021-2022 Actuals']), float(rev['2022-2023 RE']), float(rev['2023-2024 BE'])],
    'Expenditure': [float(exp['2021-2022 Actuals']), float(exp['2022-2023 RE']), float(exp['2023-2024 BE'])]
})

# Fiscal Deficit data
fd = pd.read_csv("data/raw/Fiscal_Deficit.csv")
fd_data = pd.DataFrame({
    'Year': [2021, 2022, 2023],
    'Fiscal_Deficit': [9.2, 6.7, 6.4] # From Fiscal_Deficit.csv: 2020-21 -> 9.2, 2021-22 -> 6.7, 2022-23 -> 6.4
})

# Merge all
final_df = budget_data.merge(fd_data, on='Year', how='left')
final_df = final_df.merge(gdp, on='Year', how='left')
final_df = final_df.merge(inflation, on='Year', how='left')
final_df = final_df.merge(population, on='Year', how='left')
final_df = final_df.merge(unemployment, on='Year', how='left')
final_df = final_df.merge(interest_rate, on='Year', how='left')

# Handle missing values using ffill and bfill
final_df = final_df.ffill().bfill()

# Reorder columns
final_df = final_df[['Year', 'GDP', 'Inflation', 'Population', 'Unemployment', 'Interest_Rate', 'Fiscal_Deficit', 'Revenue', 'Expenditure']]

# Save to data/processed/final_dataset.csv
final_df.to_csv("data/processed/final_dataset.csv", index=False)
print("✅ Final Dataset created successfully at data/processed/final_dataset.csv")
print(final_df)
