import json
import os

import joblib
import numpy as np
import pandas as pd
import torch
import torch.nn as nn


class LSTMModel(nn.Module):
    """Match the model definition used in scripts/train_model.py and ml_api/predict.py."""

    def __init__(self, input_size: int, hidden_size: int, output_size: int):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True)
        self.fc = nn.Linear(hidden_size, output_size)
        self.relu = nn.ReLU()

    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.relu(out[:, -1, :])
        out = self.fc(out)
        return out


def _first_existing_path(*paths: str) -> str:
    for p in paths:
        if os.path.exists(p):
            return p
    raise FileNotFoundError(f"None of these paths exist: {paths}")


def main() -> int:
    dataset_path = _first_existing_path(
        "data/processed/final_dataset.csv",
        "data/processed/FinalDataset.csv",
    )
    model_path = _first_existing_path("model/gdp_model.pth")
    scaler_path = _first_existing_path("model/scaler.pkl")

    df = pd.read_csv(dataset_path)
    # Keep this aligned with the current processed dataset headers.
    feature_cols = [
        "GDP",
        "Inflation",
        "Population",
        "Unemployment",
        "Interest_Rate",
        "Fiscal_Deficit",
        "Revenue",
        "Expenditure",
    ]
    missing = [c for c in feature_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Missing expected columns in {dataset_path}: {missing}. "
            f"Found columns: {df.columns.tolist()}"
        )

    # Evaluate the model the same way it is trained: row[t] -> predict GDP at row[t+1].
    X = df[feature_cols].to_numpy(dtype="float64")
    y_true = df["GDP"].to_numpy(dtype="float64")[1:]
    if len(y_true) < 1:
        raise ValueError(
            "Not enough rows to evaluate. Need at least 2 rows in the dataset."
        )

    scaler = joblib.load(scaler_path)
    X_scaled = scaler.transform(X)

    model = LSTMModel(input_size=len(feature_cols), hidden_size=10, output_size=1)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()

    xs = torch.tensor(X_scaled[:-1], dtype=torch.float32).unsqueeze(1)
    with torch.no_grad():
        y_pred_scaled = model(xs).cpu().numpy().reshape(-1, 1)

    # Inverse-transform only the GDP column by reconstructing a full 8-feature row.
    y_pred = scaler.inverse_transform(
        np.concatenate([y_pred_scaled, X_scaled[:-1, 1:]], axis=1)
    )[:, 0]

    mae = float(np.mean(np.abs(y_pred - y_true)))
    rmse = float(np.sqrt(np.mean((y_pred - y_true) ** 2)))
    mape = float(np.mean(np.abs((y_pred - y_true) / y_true)) * 100.0)

    report = {
        "dataset": dataset_path,
        "eval_points": int(len(y_true)),
        "metrics": {"mae": mae, "rmse": rmse, "mape_percent": mape},
        # Helpful for debugging / demo slides.
        "y_true": [float(v) for v in y_true],
        "y_pred": [float(v) for v in y_pred],
        "note": (
            "This is a tiny next-step evaluation on consecutive rows. "
            "For a meaningful accuracy estimate, expand the dataset (more years) "
            "and use a proper time-based train/validation split."
        ),
    }

    os.makedirs("outputs", exist_ok=True)
    out_path = os.path.join("outputs", "gdp_model_eval.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("GDP model evaluation written to:", out_path)
    print("Eval points:", report["eval_points"])
    print("MAE:", report["metrics"]["mae"])
    print("RMSE:", report["metrics"]["rmse"])
    print("MAPE%:", report["metrics"]["mape_percent"])
    if report["eval_points"] < 10:
        print("WARNING: Very small dataset; metrics are not statistically reliable.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

