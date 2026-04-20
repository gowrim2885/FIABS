from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
UPLOADS_DIR = PROJECT_ROOT / "data" / "uploads"

DATASET_CANDIDATES = [
    UPLOADS_DIR / "merged-csv-files.csv",
    UPLOADS_DIR / "raw_data.csv",
    PROJECT_ROOT / "data" / "processed" / "final_dataset.csv",
    PROJECT_ROOT / "data" / "dataset.csv",
]

COLUMN_MAP = {
    "actual_spending": "expenditure",
    "total_budget": "revenue",
    "inflation_rate": "inflation",
    "interest_rate": "interest_rate",
    "interest": "interest_rate",
    "fiscal_deficit": "fiscal_deficit",
    "deficit": "fiscal_deficit",
}

NUMERIC_COLUMNS = [
    "year",
    "revenue",
    "expenditure",
    "inflation",
    "population",
    "gdp",
    "gdp_share",
    "interest_rate",
    "fiscal_deficit",
]


def get_dataset_path() -> Path:
    for path in DATASET_CANDIDATES:
        if path.exists():
            return path
    raise FileNotFoundError("No FIABS dataset is available.")


def _normalize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.copy()
    normalized.columns = [str(col).strip().lower() for col in normalized.columns]
    normalized = normalized.rename(columns=COLUMN_MAP)

    if "year" not in normalized.columns:
        raise ValueError("Dataset must include a year column.")

    # Remove repeated header rows from merged CSV files.
    normalized = normalized[normalized["year"].astype(str).str.lower() != "year"].copy()

    for column in NUMERIC_COLUMNS:
        if column in normalized.columns:
            normalized[column] = pd.to_numeric(normalized[column], errors="coerce")

    if "department" in normalized.columns:
        normalized["department"] = (
            normalized["department"]
            .astype(str)
            .str.strip()
            .str.replace("_", " ", regex=False)
        )

    normalized = normalized.dropna(subset=["year"]).copy()
    normalized["year"] = normalized["year"].astype(int)

    required = [col for col in ["department", "revenue", "expenditure"] if col in normalized.columns]
    if required:
        normalized = normalized.dropna(subset=required).copy()

    if "inflation" not in normalized.columns:
        normalized["inflation"] = 0.0
    if "population" not in normalized.columns:
        normalized["population"] = normalized.groupby("year")["year"].transform(lambda _: 0)
    if "gdp" not in normalized.columns:
        normalized["gdp"] = normalized["revenue"].fillna(0) * 4.5
    if "fiscal_deficit" not in normalized.columns:
        normalized["fiscal_deficit"] = normalized["expenditure"].fillna(0) - normalized["revenue"].fillna(0)
    if "interest_rate" not in normalized.columns:
        normalized["interest_rate"] = 0.0

    normalized["budget_balance"] = normalized["revenue"].fillna(0) - normalized["expenditure"].fillna(0)
    normalized["utilization_rate"] = (
        normalized["expenditure"].fillna(0) / normalized["revenue"].replace(0, pd.NA)
    ).fillna(0)

    return normalized.sort_values(["year", "department"] if "department" in normalized.columns else ["year"]).reset_index(drop=True)


def load_dataset() -> pd.DataFrame:
    dataset_path = get_dataset_path()
    df = pd.read_csv(dataset_path, on_bad_lines="skip")
    return _normalize_dataframe(df)


def filtered_dataset(year: Optional[int] = None, department: Optional[str] = None) -> pd.DataFrame:
    df = load_dataset()
    if year is not None:
        df = df[df["year"] == int(year)]
    if department and department.lower() != "all" and "department" in df.columns:
        df = df[df["department"].str.lower() == department.lower()]
    return df.reset_index(drop=True)


def yearly_summary(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    dataset = load_dataset() if df is None else df.copy()
    grouped = (
        dataset.groupby("year", as_index=False)
        .agg(
            revenue=("revenue", "sum"),
            expenditure=("expenditure", "sum"),
            inflation=("inflation", "mean"),
            population=("population", "max"),
            gdp=("gdp", "sum"),
            budget_balance=("budget_balance", "sum"),
        )
        .sort_values("year")
    )
    return grouped.reset_index(drop=True)


def department_summary(df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    dataset = load_dataset() if df is None else df.copy()
    if "department" not in dataset.columns:
        return pd.DataFrame(columns=["department", "budget", "spending", "budget_balance", "utilization_rate"])

    grouped = (
        dataset.groupby("department", as_index=False)
        .agg(
            budget=("revenue", "sum"),
            spending=("expenditure", "sum"),
            budget_balance=("budget_balance", "sum"),
            utilization_rate=("utilization_rate", "mean"),
        )
        .sort_values("spending", ascending=False)
    )
    return grouped.reset_index(drop=True)


def save_uploaded_dataset(source_path: str) -> Path:
    df = pd.read_csv(source_path, on_bad_lines="skip")
    normalized = _normalize_dataframe(df)
    os.makedirs(UPLOADS_DIR, exist_ok=True)
    target = UPLOADS_DIR / "merged-csv-files.csv"
    normalized.to_csv(target, index=False)
    normalized.to_csv(UPLOADS_DIR / "raw_data.csv", index=False)
    return target
