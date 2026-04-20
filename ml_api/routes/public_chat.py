from typing import Optional

from fastapi import APIRouter
from pydantic import BaseModel

from services import chatbot
from services.dataset_loader import filtered_dataset, load_dataset


router = APIRouter(prefix="/public/chatbot", tags=["public"])


class ChatRequest(BaseModel):
    question: str
    year: Optional[int] = None


def get_fiscal_data(year: Optional[int] = None):
    df = load_dataset()
    selected_year = int(year) if year is not None else int(df["year"].max())
    year_df = filtered_dataset(year=selected_year)
    if year_df.empty:
        return None, None

    dept_data = [
        {
            "department": row["department"],
            "budget": float(row["revenue"]),
            "spending": float(row["expenditure"]),
        }
        for _, row in year_df.iterrows()
    ]

    top_row = year_df.sort_values("expenditure", ascending=False).iloc[0]
    context = {
        "year": selected_year,
        "inflation": float(year_df["inflation"].mean()),
        "revenue": float(year_df["revenue"].sum()),
        "expenditure": float(year_df["expenditure"].sum()),
        "deficit": float((year_df["expenditure"] - year_df["revenue"]).sum()),
        "gdp": float(year_df["gdp"].sum()),
        "top_department": top_row["department"],
        "available_years": sorted(df["year"].astype(int).unique().tolist()),
    }
    return dept_data, context


@router.post("/chat")
async def public_chat(request: ChatRequest):
    try:
        data, context = get_fiscal_data(request.year)
        if data is None:
            return {"answer": "I do not have enough data to answer that year yet."}
        return {"answer": chatbot.chatbot_response(request.question, data, context)}
    except Exception as exc:
        return {"answer": f"I hit a data error while answering that question: {exc}"}
