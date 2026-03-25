import pandas as pd
import matplotlib.pyplot as plt

# Load final dataset
df = pd.read_csv("data/processed/final_dataset.csv")

print("✅ Dataset Loaded")
print(df.head())

# -----------------------------
# GDP TREND
# -----------------------------

gdp_trend = df[['Year', 'GDP']].drop_duplicates()

plt.figure()
plt.plot(gdp_trend['Year'], gdp_trend['GDP'])
plt.title("GDP Growth Over Years")
plt.xlabel("Year")
plt.ylabel("GDP")
plt.show()

# -----------------------------
# INFLATION TREND
# -----------------------------

inflation_trend = df[['Year', 'Inflation']].drop_duplicates()

plt.figure()
plt.plot(inflation_trend['Year'], inflation_trend['Inflation'])
plt.title("Inflation Trend")
plt.xlabel("Year")
plt.ylabel("Inflation")
plt.show()

# -----------------------------
# BUDGET ANALYSIS
# -----------------------------

budget_trend = df[df['Parameter'] == 'Revenue Receipts']

plt.figure()
plt.plot(budget_trend['Year'], budget_trend['Amount'])
plt.title("Revenue Receipts Over Years")
plt.xlabel("Year")
plt.ylabel("Amount")
plt.show()