import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense

# -----------------------------
# Step 1: Load dataset
# -----------------------------
df = pd.read_csv("data/processed/final_dataset.csv")

print("Columns:", df.columns)
print("Available Parameters:", df["Parameter"].unique())

# -----------------------------
# Step 2: Filter data
# -----------------------------
selected_param = "Revenue Receipts"   # 🔥 change if needed

data = df[df["Parameter"] == selected_param]

if data.empty:
    raise ValueError(f"No data found for {selected_param}")

# -----------------------------
# Step 3: Aggregate correctly
# -----------------------------
data = data.groupby("Year").agg({
    "Amount": "sum",
    "GDP": "mean",
    "Inflation": "mean"
}).reset_index()

print("\nProcessed Data:")
print(data)

# -----------------------------
# Step 4: Prepare multi-feature data
# -----------------------------
features = data[["Amount", "GDP", "Inflation"]]

scaler = MinMaxScaler()
scaled_data = scaler.fit_transform(features)

# -----------------------------
# Step 5: Create sequences
# -----------------------------
time_steps = 3

if len(scaled_data) <= time_steps:
    time_steps = len(scaled_data) - 1

X, y = [], []

for i in range(time_steps, len(scaled_data)):
    X.append(scaled_data[i-time_steps:i])
    y.append(scaled_data[i][0])  # predict Amount only

X, y = np.array(X), np.array(y)

print("\nShapes:")
print("X:", X.shape)
print("y:", y.shape)

if len(X) == 0:
    raise ValueError("Not enough data for training")

# -----------------------------
# Step 6: Build model
# -----------------------------
model = Sequential([
    LSTM(64, activation='relu', input_shape=(X.shape[1], X.shape[2])),
    Dense(1)
])

model.compile(optimizer='adam', loss='mse')

print("\nTraining model...")
model.fit(X, y, epochs=30, batch_size=1, verbose=1)

# -----------------------------
# Step 7: Predict future
# -----------------------------
future_steps = 5
last_sequence = scaled_data[-time_steps:]

predictions = []

for _ in range(future_steps):
    input_seq = last_sequence.reshape(1, time_steps, 3)

    pred = model.predict(input_seq, verbose=0)
    predictions.append(pred[0][0])

    # keep GDP & Inflation same (last known values)
    next_step = np.array([pred[0][0], last_sequence[-1][1], last_sequence[-1][2]])
    last_sequence = np.vstack((last_sequence[1:], next_step))

# -----------------------------
# Step 8: Inverse transform
# -----------------------------
pred_array = np.zeros((len(predictions), 3))
pred_array[:, 0] = predictions

predictions = scaler.inverse_transform(pred_array)[:, 0]

# -----------------------------
# Step 9: Output
# -----------------------------
print(f"\n🔮 Predictions for {selected_param}:")
for i, val in enumerate(predictions):
    print(f"Year {data['Year'].max() + i + 1}: {val:,.2f}")

# -----------------------------
# Step 10: Plot
# -----------------------------
plt.figure(figsize=(10, 5))

# Historical
plt.plot(data["Year"], data["Amount"], marker='o', label="Historical")

# Future
future_years = [data["Year"].max() + i for i in range(1, future_steps + 1)]
plt.plot(future_years, predictions, marker='x', linestyle='--', label="Predicted")

plt.xlabel("Year")
plt.ylabel(selected_param)
plt.title(f"{selected_param} Forecast (Multi-feature LSTM)")
plt.legend()
plt.grid(True)

plt.show()