import pandas as pd
import os

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

RAW_DATA_PATH = "data/uploads/raw_data.csv"

def generate_recommendations():
    """Generates fiscal recommendations based on current dataset trends."""
    if not os.path.exists(RAW_DATA_PATH):
        return {"error": "Dataset not found."}

    df = pd.read_csv(RAW_DATA_PATH)
    df.columns = [c.strip().lower() for c in df.columns]
    
    # Standardize column mapping
    if "actual_spending" in df.columns:
        df = df.rename(columns={"actual_spending": "expenditure", "total_budget": "revenue", "inflation_rate": "inflation"})

    latest_year = df["year"].max()
    df_latest = df[df["year"] == latest_year]
    
    recommendations = []

    # 1. Spending Efficiency Recommendation
    df_latest["utilization"] = (df_latest["expenditure"] / df_latest["revenue"]) * 100
    over_budget = df_latest[df_latest["utilization"] > 100]
    under_utilized = df_latest[df_latest["utilization"] < 70]

    if not over_budget.empty:
        depts = ", ".join(over_budget["department"].tolist())
        recommendations.append({
            "category": "Fiscal Discipline",
            "priority": "High",
            "message": f"Departments ({depts}) exceeded their budget. Recommend a strict audit of operational expenses."
        })

    if not under_utilized.empty:
        depts = ", ".join(under_utilized["department"].tolist())
        recommendations.append({
            "category": "Resource Allocation",
            "priority": "Medium",
            "message": f"Departments ({depts}) have low utilization (<70%). Consider reallocating unused funds to high-impact sectors."
        })

    # 2. Inflation & Growth Recommendation
    avg_inflation = df_latest["inflation"].mean()
    if avg_inflation > 6.0:
        recommendations.append({
            "category": "Economic Stability",
            "priority": "High",
            "message": f"Inflation is high ({avg_inflation:.1f}%). Suggest reducing non-essential government spending to curb inflationary pressure."
        })
    else:
        recommendations.append({
            "category": "Economic Growth",
            "priority": "Low",
            "message": "Inflation is stable. Current fiscal environment is conducive for long-term infrastructure investment."
        })

    # 3. Top Sector Recommendation
    top_dept = df_latest.groupby("department")["expenditure"].sum().idxmax()
    recommendations.append({
        "category": "Strategic Focus",
        "priority": "Information",
        "message": f"{top_dept} remains the primary spending driver. Evaluate if this aligns with the 5-year strategic national goals."
    })

    # 4. LLM Strategic Insight (Optional)
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key and OpenAI:
        try:
            client = OpenAI(api_key=api_key)
            # Create a small summary for the LLM
            summary_stats = df_latest.groupby("department")[["revenue", "expenditure"]].sum().to_string()
            
            prompt = f"""
            You are a senior fiscal policy advisor. Based on the following departmental budget vs spending data for the year {latest_year}, 
            provide one high-level strategic recommendation (max 40 words).
            
            Data Summary:
            {summary_stats}
            
            Output format: A single concise sentence starting with 'AI Strategy:'.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,
                max_tokens=100
            )
            ai_message = response.choices[0].message.content.strip()
            recommendations.append({
                "category": "AI Strategic Advice",
                "priority": "Information",
                "message": ai_message
            })
        except Exception:
            pass # Fallback to rule-based only if LLM fails

    return recommendations
