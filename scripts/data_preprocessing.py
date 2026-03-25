import pandas as pd

# -----------------------------
# LOAD DATASETS
# -----------------------------

budget = pd.read_excel("data/raw/budget_glance.xlsx")
exp = pd.read_csv("data/raw/category_expenditure.csv")
cpse = pd.read_csv("data/raw/cpse_expenditure.csv")

print("✅ Budget Data")
print(budget.head())

print("\n✅ Expenditure Data")
print(exp.head())

print("\n✅ CPSE Data")
print(cpse.head())


# -----------------------------
# LOAD GDP & INFLATION
# -----------------------------

gdp = pd.read_csv("data/raw/API_GDP.csv", skiprows=4)
inflation = pd.read_csv("data/raw/API_INFLATION.csv", skiprows=4)

print("\n✅ GDP Data")
print(gdp.head())

print("\n✅ Inflation Data")
print(inflation.head())

# Filter only India
gdp = gdp[gdp['Country Name'] == 'India']

print("\n✅ GDP - India Only")
print(gdp.head())

# Filter only India
inflation = inflation[inflation['Country Name'] == 'India']

print("\n✅ Inflation - India Only")
print(inflation.head())

# -----------------------------
# CLEAN & TRANSFORM GDP
# -----------------------------

gdp = gdp.drop(columns=[
    'Country Name',
    'Country Code',
    'Indicator Name',
    'Indicator Code',
    'Unnamed: 70'
], errors='ignore')

gdp = gdp.melt(var_name="Year", value_name="GDP")

gdp['Year'] = gdp['Year'].astype(int)

gdp = gdp.dropna()

print("\n✅ Cleaned GDP")
print(gdp.head())

# -----------------------------
# CLEAN & TRANSFORM INFLATION
# -----------------------------

inflation = inflation.drop(columns=[
    'Country Name',
    'Country Code',
    'Indicator Name',
    'Indicator Code',
    'Unnamed: 70'
], errors='ignore')

inflation = inflation.melt(var_name="Year", value_name="Inflation")

inflation['Year'] = inflation['Year'].astype(int)

inflation = inflation.dropna()

print("\n✅ Cleaned Inflation")
print(inflation.head())


print("\n🔍 Budget Columns:")
print(budget.columns)





# -----------------------------
# FIX COLUMN NAMES
# -----------------------------

# Clean column names
budget.columns = budget.columns.str.strip()

# Rename the merged column
budget = budget.rename(columns={
    'SI. No.        Parameters': 'Parameter'
})

# Drop unwanted index numbers inside values (like "1.", "2.")
budget['Parameter'] = budget['Parameter'].str.replace(r'^\d+\.\s*', '', regex=True)

print("\n✅ Fixed Budget Columns")
print(budget.head())

# -----------------------------
# TRANSFORM BUDGET
# -----------------------------

budget = budget.melt(id_vars=['Parameter'], var_name='Year', value_name='Amount')

budget['Year'] = budget['Year'].str.extract(r'(\d{4})').astype(int)

budget = budget.dropna()

print("\n✅ Cleaned Budget Data")
print(budget.head())



# -----------------------------
# CLEAN & TRANSFORM EXPENDITURE
# -----------------------------

exp.columns = exp.columns.str.strip()

exp = exp.dropna(subset=['Category'])

exp = exp[~exp['Category'].str.contains("TOTAL", case=False, na=False)]

exp = exp.melt(id_vars=['Category'], var_name='Year', value_name='Expenditure')

# FIX STARTS HERE
exp['Year'] = exp['Year'].str.extract(r'(\d{4})')
exp = exp.dropna(subset=['Year'])
exp['Year'] = exp['Year'].astype(int)
# FIX ENDS HERE

exp = exp.dropna()

print("\n✅ Cleaned Expenditure Data")
print(exp.head())



# -----------------------------
# CLEAN & TRANSFORM CPSE
# -----------------------------

# Clean column names
cpse.columns = cpse.columns.str.strip()

# Drop serial column
cpse = cpse.drop(columns=['Sl. No.'], errors='ignore')

# Convert wide → long
cpse = cpse.melt(var_name='Year', value_name='Value')

# Extract year
cpse['Year'] = cpse['Year'].str.extract(r'(\d{4})')

# Remove invalid rows
cpse = cpse.dropna(subset=['Year'])

# Convert to int
cpse['Year'] = cpse['Year'].astype(int)

# Drop null values
cpse = cpse.dropna()

print("\n✅ Cleaned CPSE Data")
print(cpse.head())

# -----------------------------
# MERGE GDP & INFLATION
# -----------------------------

macro = pd.merge(gdp, inflation, on='Year', how='inner')

print("\n✅ Macro Data (GDP + Inflation)")
print(macro.head())

# -----------------------------
# MERGE WITH BUDGET
# -----------------------------

final_df = pd.merge(budget, macro, on='Year', how='left')

print("\n✅ After adding macro data")
print(final_df.head())

# -----------------------------
# SAVE FINAL DATASET
# -----------------------------

final_df.to_csv("data/processed/final_dataset.csv", index=False)

print("\n🎉 Final dataset saved successfully!")