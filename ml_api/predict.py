import numpy as np
import torch
import torch.nn as nn
import joblib
import os

# Re-define the LSTM model class to load the state dict
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

# Constants
FEATURES = ["GDP", "Inflation", "Population", "Unemployment", "Interest_Rate", "Fiscal_Deficit", "Revenue", "Expenditure"]
INPUT_SIZE = len(FEATURES)
HIDDEN_SIZE = 10
OUTPUT_SIZE = 1

# Base directory for models
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "../model/gdp_model.pth")
SCALER_PATH = os.path.join(BASE_DIR, "../model/scaler.pkl")

# Load model and scaler once
scaler = joblib.load(SCALER_PATH)
model = LSTMModel(INPUT_SIZE, HIDDEN_SIZE, OUTPUT_SIZE)
model.load_state_dict(torch.load(MODEL_PATH))
model.eval()

def predict_gdp(input_data):
    """
    input_data: list of 8 features in order:
    [GDP, Inflation, Population, Unemployment, Interest_Rate, Fiscal_Deficit, Revenue, Expenditure]
    """
    # Reshape and scale input data
    data = np.array(input_data).reshape(1, -1)
    scaled_data = scaler.transform(data)
    
    # Convert to PyTorch tensor and reshape (samples, time_steps, features)
    input_tensor = torch.tensor(scaled_data, dtype=torch.float32).reshape(1, 1, -1)
    
    # Predict
    with torch.no_grad():
        prediction_scaled = model(input_tensor).detach().numpy()
        
    # Inverse transform
    # Using concatenation ensures we map correctly back to the GDP column
    prediction_actual = scaler.inverse_transform(
        np.concatenate([prediction_scaled, scaled_data[:, 1:]], axis=1)
    )[:, 0]
    
    return float(prediction_actual[0])

if __name__ == "__main__":
    # Test prediction
    sample_input = [3.6e12, 5.6, 1.4e9, 4.2, 6.0, 6.4, 2.6e6, 4.5e6]
    result = predict_gdp(sample_input)
    print(f"Test Predicted GDP: {result}")
