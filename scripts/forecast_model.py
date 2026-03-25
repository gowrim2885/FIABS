import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.tsa.arima.model import ARIMA

# Load dataset
df = pd.read_csv("data/processed/final_dataset.csv")

print("✅ Data Loaded")
print(df.head())



# Filter data
data = df[df['Parameter'] == 'Revenue Receipts']

# Group by year
data = data.groupby('Year')['Amount'].sum().reset_index()

print("\n✅ Forecast Data")
print(data)

# Filter data
data = df[df['Parameter'] == 'Revenue Receipts']

# Group by year
data = data.groupby('Year')['Amount'].sum().reset_index()

print("\n✅ Forecast Data")
print(data)

# Convert to time series
ts = data.set_index('Year')['Amount']

# Build model
model = ARIMA(ts, order=(1,1,1))

model_fit = model.fit()

print("\n✅ Model Trained")

forecast = model_fit.forecast(steps=5)

print("\n🔮 Forecasted Values:")
print(forecast)


# Create future years
future_years = [data['Year'].max() + i for i in range(1,6)]

plt.figure()
plt.plot(data['Year'], data['Amount'], label='Actual')
plt.plot(future_years, forecast, label='Forecast')
plt.legend()
plt.title("Revenue Forecast")
plt.xlabel("Year")
plt.ylabel("Amount")
plt.show()


