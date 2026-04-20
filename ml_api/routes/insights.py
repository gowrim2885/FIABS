from fastapi import APIRouter

from services.dataset_loader import filtered_dataset, yearly_summary


router = APIRouter(prefix="/insights", tags=["insights"])


@router.get("/")
def get_insights():
    try:
        df = filtered_dataset()
    except FileNotFoundError:
        return {"error": "Raw data not found. Please upload a dataset first."}

    top_dept = df.groupby("department")["expenditure"].sum().idxmax()
    total_spending = df["expenditure"].sum()
    avg_inflation = df["inflation"].mean()

    return {
        "top_department": top_dept,
        "total_spending": float(total_spending),
        "average_inflation": float(avg_inflation),
    }


@router.get("/kpis")
def get_kpis(year: int):
    try:
        df = filtered_dataset(year=year)
    except FileNotFoundError:
        return {"error": "Dataset not found"}

    if df.empty:
        return {"error": f"No data for year {year}"}

    return {
        "total_spending": float(df["expenditure"].sum()),
        "avg_inflation": float(df["inflation"].mean()),
        "top_department": df.groupby("department")["expenditure"].sum().idxmax(),
    }


@router.get("/gdp-trend")
def gdp_trend():
    try:
        yearly = yearly_summary()
    except FileNotFoundError:
        return {"error": "Raw data not found"}

    return {
        "years": yearly["year"].astype(int).tolist(),
        "gdp": yearly["gdp"].astype(float).tolist(),
    }
