import io
import os

import pandas as pd
from fastapi import APIRouter, File, Header, HTTPException, UploadFile
from pydantic import BaseModel

from services.anomaly import detect_anomalies
from services.data_processor import process_data
from services.dataset_loader import filtered_dataset
from services.insights import generate_insights
from services.predict import predict_gdp
from services.train_model import train_model
from services.budget_predictor import predict_future_budget
from services.recommendation_engine import generate_recommendations


router = APIRouter(prefix="/analyst", tags=["analyst"])

RAW_DATA_PATH = "data/uploads/raw_data.csv"
MERGED_DATASET_PATH = "data/uploads/merged-csv-files.csv"
REQUIRED_COLUMNS = ["year", "department", "revenue", "expenditure", "inflation"]


class PredictRequest(BaseModel):
    revenue: float
    inflation: float


def require_analyst(role: str | None):
    if role != "analyst":
        raise HTTPException(status_code=403, detail="Access denied. Analyst role required.")


def normalize_uploaded_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [c.strip().lower() for c in df.columns]
    df = df[df["year"].astype(str).str.lower() != "year"].copy()
    df = df.rename(
        columns={
            "actual_spending": "expenditure",
            "total_budget": "revenue",
            "inflation_rate": "inflation",
        }
    )

    for col in ["year", "revenue", "expenditure", "inflation", "population", "gdp_share"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "department" in df.columns:
        df["department"] = df["department"].astype(str).str.strip().str.replace("_", " ", regex=False)

    df = df.dropna(subset=["year", "department", "revenue", "expenditure", "inflation"]).copy()
    df["year"] = df["year"].astype(int)
    return df


@router.post("/upload")
async def upload_data(file: UploadFile = File(...), role: str = Header(None)):
    require_analyst(role)

    try:
        contents = await file.read()
        df = pd.read_csv(io.BytesIO(contents), on_bad_lines="skip")
        df = normalize_uploaded_dataframe(df)

        missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing:
            return {"error": f"Missing required columns: {missing}"}
        if df.empty:
            return {"error": "The uploaded file did not contain valid fiscal rows after cleaning."}
        if (df["year"] < 0).any():
            return {"error": "Year cannot be negative"}

        os.makedirs(os.path.dirname(RAW_DATA_PATH), exist_ok=True)
        df.to_csv(RAW_DATA_PATH, index=False)
        df.to_csv(MERGED_DATASET_PATH, index=False)
        process_data()

        return {
            "message": f"Dataset uploaded successfully with {len(df)} cleaned rows across {df['year'].nunique()} years."
        }
    except Exception as exc:
        return {"error": str(exc)}


@router.post("/train")
async def train(role: str = Header(None)):
    require_analyst(role)
    result = train_model()
    return {"message": result}


@router.post("/predict")
async def predict(req: PredictRequest, role: str = Header(None)):
    require_analyst(role)
    gdp = predict_gdp(req.revenue, req.inflation)
    if isinstance(gdp, str) and gdp.startswith("Error"):
        return {"error": gdp}
    return {"predicted_gdp": gdp}


@router.get("/predict-budget")
def get_budget_forecast(role: str = Header(None)):
    require_analyst(role)
    return predict_future_budget()

@router.get("/recommendations")
def get_recommendations(role: str = Header(None)):
    require_analyst(role)
    return generate_recommendations()

@router.get("/anomalies")
async def anomalies(role: str = Header(None)):
    require_analyst(role)
    return {"anomalies": detect_anomalies()}


@router.get("/insights")
async def insights(role: str = Header(None)):
    require_analyst(role)
    latest_year = int(filtered_dataset()["year"].max())
    return {
        "insights": generate_insights(),
        "latest_year": latest_year,
    }
