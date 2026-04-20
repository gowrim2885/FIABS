import pandas as pd
from sklearn.ensemble import IsolationForest
import joblib
import os

# Configuration
data_path = "data/processed/final_dataset.csv"
model_path = "model/anomaly_model.pkl"
os.makedirs("model", exist_ok=True)

# 1. Load dataset
df = pd.read_csv(data_path)

# Standardize column names to lowercase
df.columns = [c.strip().lower() for c in df.columns]

# 2. Select features (matching the column names in final_dataset.csv)
# Map provided feature names to actual CSV column names
feature_mapping = {
    "gdp": "gdp",
    "inflation": "inflation",
    "population": "population",
    "unemployment": "unemployment",
    "interest": "interest_rate",
    "deficit": "fiscal_deficit",
    "revenue": "revenue",
    "expenditure": "expenditure"
}

features_to_use = [feature_mapping[f] for f in ["gdp", "inflation", "population", "unemployment", "interest", "deficit", "revenue", "expenditure"]]
data = df[features_to_use]

# 3. Train model
# Using a slightly higher contamination if data is small, but sticking to 0.05 as requested
model = IsolationForest(contamination=0.05, random_state=42)
model.fit(data)

# 4. Save model
joblib.dump(model, model_path)

print(f"Anomaly model saved successfully to {model_path}!")
