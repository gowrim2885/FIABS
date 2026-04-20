import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import torch
import torch.nn as nn
import torch.optim as optim
import matplotlib.pyplot as plt
import os
import joblib

# Configuration
dataset_path = "data/dataset.csv"
default_path = "data/processed/final_dataset.csv"
outputs_dir = "outputs"
model_dir = "model"

# Create necessary directories
os.makedirs(outputs_dir, exist_ok=True)
os.makedirs(model_dir, exist_ok=True)

# 1. Load dataset
required_features = ["gdp", "inflation", "population", "unemployment", "interest_rate", "fiscal_deficit", "revenue", "expenditure"]

def load_data():
    if os.path.exists(dataset_path):
        try:
            temp_df = pd.read_csv(dataset_path)
            temp_df.columns = [c.strip().lower() for c in temp_df.columns]
            # Check if at least some required columns exist (simple heuristic)
            if all(feat in temp_df.columns for feat in ["gdp", "fiscal_deficit"]):
                print(f"Using uploaded dataset: {dataset_path}")
                return temp_df
            else:
                print(f"Uploaded dataset {dataset_path} is incomplete. Falling back.")
        except Exception as e:
            print(f"Error loading {dataset_path}: {e}. Falling back.")
    
    print(f"Using default dataset: {default_path}")
    df = pd.read_csv(default_path)
    df.columns = [c.strip().lower() for c in df.columns]
    return df

df = load_data()

# 2. Select relevant features
column_mapping = {
    "gdp": "gdp",
    "inflation": "inflation",
    "population": "population",
    "unemployment": "unemployment",
    "interest_rate": "interest_rate",
    "fiscal_deficit": "fiscal_deficit",
    "revenue": "revenue",
    "expenditure": "expenditure"
}

fallback_mapping = {
    "interest_rate": "interest",
    "fiscal_deficit": "deficit"
}

for feat, col in column_mapping.items():
    if col not in df.columns:
        if feat in fallback_mapping and fallback_mapping[feat] in df.columns:
            df[col] = df[fallback_mapping[feat]]
        else:
            print(f"Warning: Column '{col}' not found. Filling with 0.0")
            df[col] = 0.0

features = ["gdp", "inflation", "population", "unemployment", "interest_rate", "fiscal_deficit", "revenue", "expenditure"]
data = df[features].values

# 3. Normalize data
scaler = MinMaxScaler()
data_scaled = scaler.fit_transform(data)

# 4. Create sequences
X = []
y = []
for i in range(len(data_scaled) - 1):
    X.append(data_scaled[i])
    y.append(data_scaled[i + 1][0])

X = np.array(X, dtype=np.float32)
y = np.array(y, dtype=np.float32)

# 5. Reshape for PyTorch
if len(X.shape) < 2:
    print("Error: Not enough data to train. Need at least 2 rows.")
    exit(1)

X_tensor = torch.tensor(X).reshape(X.shape[0], 1, X.shape[1])
y_tensor = torch.tensor(y).reshape(-1, 1)

print("Input Shape (X):", X_tensor.shape)
print("Output Shape (y):", y_tensor.shape)

# 6. Build LSTM model
class LSTMModel(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(LSTMModel, self).__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.relu(out[:, -1, :])
        out = self.fc(out)
        return out

input_size = len(features)
hidden_size = 10
output_size = 1

model = LSTMModel(input_size, hidden_size, output_size)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 7. Train
print("Training the model for 100 epochs...")
model.train()
for epoch in range(100):
    optimizer.zero_grad()
    outputs = model(X_tensor)
    loss = criterion(outputs, y_tensor)
    loss.backward()
    optimizer.step()
    if (epoch + 1) % 20 == 0:
        print(f"Epoch [{epoch+1}/100], Loss: {loss.item():.6f}")

print("Training complete.")

# 8. Predict
model.eval()
with torch.no_grad():
    last_year_data = torch.tensor(data_scaled[-1], dtype=torch.float32).reshape(1, 1, -1)
    prediction_scaled = model(last_year_data).numpy()

# FINAL FIX: Use full feature structure for inverse transform
dummy = [0] * 8 
dummy[0] = prediction_scaled[0, 0]   # GDP position (index 0)

# Convert to 2D 
dummy_2d = [dummy] 

# Inverse transform 
prediction_actual = scaler.inverse_transform(dummy_2d)[0][0]

print(f"Predicted GDP for 2024: ${prediction_actual:,.2f}")

# 9. Visualization
years = df["year"].values if "year" in df.columns else np.arange(len(df))
gdp_actual = df["gdp"].values

# Robustly determine next year for plotting
try:
    # Handle strings like "2020-21" by taking the first 4 chars
    last_year_str = str(years[-1])
    if '-' in last_year_str:
        last_year_val = int(last_year_str.split('-')[0])
    else:
        last_year_val = int(float(last_year_str))
    next_year = last_year_val + 1
except:
    next_year = len(years) 

plt.figure(figsize=(10, 6))
plt.plot(years, gdp_actual, marker='o', linestyle='-', color='b', label="Actual GDP")
plt.scatter(next_year, prediction_actual, color='r', marker='*', s=200, label="Predicted GDP (2024)")
plt.title("GDP Forecast for 2024 (FIABS System)")
plt.xlabel("Year")
plt.ylabel("GDP (USD)")
plt.xticks(np.append(years, next_year))
plt.legend()
plt.grid(True, linestyle='--', alpha=0.7)
plt.savefig(os.path.join(outputs_dir, "gdp_prediction.png"))

# 10. Save
torch.save(model.state_dict(), os.path.join(model_dir, "gdp_model.pth"))
joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
print("Model and scaler saved successfully to model/ directory!")
