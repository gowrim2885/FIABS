import os
from fastapi import APIRouter, HTTPException
from services.dataset_loader import department_summary, filtered_dataset, load_dataset, yearly_summary

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

router = APIRouter(prefix="/public", tags=["public"])


@router.get("/data")
async def get_all_data():
    try:
        df = load_dataset()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    summary = yearly_summary(df)
    public_rows = []
    for _, row in df.iterrows():
        public_rows.append(
            {
                "year": int(row["year"]),
                "department": row.get("department", "Unknown"),
                "budget": float(row.get("revenue", 0)),
                "spending": float(row.get("expenditure", 0)),
                "inflation": float(row.get("inflation", 0)),
                "budget_balance": float(row.get("budget_balance", 0)),
                "utilization_rate": float(row.get("utilization_rate", 0)),
            }
        )

    return {
        "years": summary["year"].astype(int).tolist(),
        "gdp_trend": summary["gdp"].astype(float).tolist(),
        "yearly_summary": summary.to_dict(orient="records"),
        "data": public_rows,
    }


@router.get("/filtered-data")
def get_filtered(year: int | None = None, department: str | None = None):
    try:
        df = filtered_dataset(year=year, department=department)
    except FileNotFoundError:
        return {"error": "Dataset not found"}
    return df.to_dict(orient="records")


@router.get("/summary")
def get_summary(year: int | None = None):
    try:
        df = filtered_dataset(year=year)
    except FileNotFoundError:
        return {"error": "Dataset not found"}

    if df.empty:
        return {"error": "No records available for the selected filters"}

    top_spend_row = df.sort_values("expenditure", ascending=False).iloc[0]
    best_balance_row = df.sort_values("budget_balance", ascending=False).iloc[0]
    overrun_row = df.sort_values("utilization_rate", ascending=False).iloc[0]
    departments = department_summary(df)
    
    selected_year = int(df["year"].max())
    
    insights = [
        f"{top_spend_row['department']} received the highest spending in the selected view.",
        f"{overrun_row['department']} is using {overrun_row['utilization_rate'] * 100:.1f}% of its allocated budget.",
        f"Average inflation for the selected view is {df['inflation'].mean():.2f}%.",
    ]

    # Optional: Enhance with AI Narrative
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and OpenAI:
        try:
            client = OpenAI(api_key=api_key)
            prompt = f"""
            You are a public transparency officer. Explain the fiscal state of {selected_year} based on:
            - Top Spending: {top_spend_row['department']}
            - Avg Inflation: {df['inflation'].mean():.2f}%
            - Overall Balance: {df['revenue'].sum() - df['expenditure'].sum():,.0f}
            
            Keep it to 2 very short, readable sentences for a public dashboard.
            """
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
                max_tokens=80
            )
            ai_narrative = response.choices[0].message.content.strip()
            # Replace the middle insight with AI narrative for a more professional feel
            insights[1] = ai_narrative
        except Exception:
            pass

    return {
        "selected_year": selected_year,
        "top_department": top_spend_row["department"],
        "total_budget": float(df["revenue"].sum()),
        "total_spending": float(df["expenditure"].sum()),
        "average_inflation": float(df["inflation"].mean()),
        "avg_utilization_rate": float(df["utilization_rate"].mean()),
        "largest_budget_gap_department": best_balance_row["department"],
        "most_overspent_department": overrun_row["department"],
        "insights": insights,
        "departments": departments.head(8).to_dict(orient="records"),
    }
