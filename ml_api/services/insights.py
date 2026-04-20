from services.dataset_loader import filtered_dataset


def generate_insights():
    try:
        df = filtered_dataset()
    except FileNotFoundError:
        return ["No dataset available for insights."]

    if df.empty:
        return ["No dataset available for insights."]

    latest_year = int(df["year"].max())
    latest = df[df["year"] == latest_year]
    avg_inflation = latest["inflation"].mean()
    top_department = latest.groupby("department")["expenditure"].sum().idxmax()
    total_spending = latest["expenditure"].sum()

    return [
        f"Average inflation in {latest_year} is {avg_inflation:.2f}%.",
        f"{top_department} is the highest-spending department in {latest_year}.",
        f"Total spending in {latest_year} is ${total_spending:,.0f}.",
    ]
