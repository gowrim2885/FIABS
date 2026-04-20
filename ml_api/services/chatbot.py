from __future__ import annotations

import os
from typing import Any
from services.llm_chatbot import generate_llm_response

def _format_money(value: float) -> str:
    return f"${value:,.0f}"

def _find_department(question: str, data: list[dict[str, Any]]) -> dict[str, Any] | None:
    q = question.lower()
    for row in data:
        department = str(row.get("department", "")).lower()
        if department and department in q:
            return row
    return None

def chatbot_response(question: str, data: list[dict[str, Any]], context: dict[str, Any]) -> str:
    if not data:
        return "I do not have enough fiscal data loaded yet. Please upload or connect a dataset first."

    # 1. Try LLM first if API key exists
    if os.getenv("OPENAI_API_KEY"):
        llm_answer = generate_llm_response(question, data, context)
        # If LLM returns a valid answer (not the fallback error message), return it
        if "AI service is unavailable" not in llm_answer:
            return llm_answer

    # 2. Rule-based Fallback / Local Engine
    q = question.lower().strip()
    year = context.get("year")
    available_years = context.get("available_years", [])
    
    # Check if a different year was mentioned in the question
    for y in available_years:
        if str(y) in q and int(y) != year:
            return f"I see you mentioned {y}. Please select {y} from the year dropdown to view and chat about that specific year's data."

    top_department = context.get("top_department", "the top department")
    total_budget = float(context.get("revenue", 0))
    total_spending = float(context.get("expenditure", 0))
    inflation = float(context.get("inflation", 0))
    balance = total_budget - total_spending

    # 🔥 INTENT: Specific Department Check
    department_row = _find_department(q, data)
    if department_row:
        dept = department_row["department"]
        budget = float(department_row.get("budget", 0))
        spending = float(department_row.get("spending", 0))
        utilization = (spending / budget * 100) if budget else 0
        return (
            f"In {year}, {dept} had a budget of {_format_money(budget)} and spending of {_format_money(spending)}. "
            f"This represents {utilization:.1f}% utilization, which is {'over' if spending > budget else 'within'} the allocated budget."
        )

    # 🔥 INTENT: Highest/Top
    if any(word in q for word in ["highest", "top", "largest", "most", "maximum"]) and any(
        word in q for word in ["budget", "spending", "department", "allocation", "expenditure"]
    ):
        top_row = max(data, key=lambda row: float(row.get("spending", row.get("expenditure", 0))))
        return (
            f"The {top_row['department']} department leads the {year} budget with the highest spending of "
            f"{_format_money(float(top_row.get('spending', top_row.get('expenditure', 0))))}."
        )

    # 🔥 INTENT: Lowest/Smallest
    if any(word in q for word in ["lowest", "smallest", "least", "minimum"]) and any(
        word in q for word in ["budget", "spending", "department", "allocation", "expenditure"]
    ):
        low_row = min(data, key=lambda row: float(row.get("spending", row.get("expenditure", 0))))
        return (
            f"The {low_row['department']} department has the lowest spending in {year} at "
            f"{_format_money(float(low_row.get('spending', low_row.get('expenditure', 0))))}."
        )

    # 🔥 INTENT: Inflation
    if "inflation" in q:
        return f"The average inflation rate for {year} is {inflation:.2f}%, according to the national fiscal dataset."

    # 🔥 INTENT: Deficit/Balance
    if any(word in q for word in ["deficit", "balance", "surplus", "debt"]):
        label = "surplus" if balance >= 0 else "deficit"
        return f"For the {year} fiscal year, the records show a budget {label} of {_format_money(abs(balance))}."

    # 🔥 INTENT: Summary/Insight
    if any(word in q for word in ["summary", "overview", "insight", "how was", "tell me", "say something", "allocation", "performance", "details", "budget"]):
        return (
            f"Here is the fiscal summary for {year}: The total budget was {_format_money(total_budget)} with a total actual spending of {_format_money(total_spending)}. "
            f"Inflation averaged {inflation:.2f}%, and {top_department} was the primary spending sector. "
            f"The overall budget balance for the year resulted in a {'surplus' if balance >= 0 else 'deficit'} of {_format_money(abs(balance))}."
        )

    # 🔥 INTENT: Data Availability
    if any(word in q for word in ["year", "data", "available", "history", "records"]):
        years_text = ", ".join(str(item) for item in available_years)
        return f"I can provide detailed fiscal analysis for the following years: {years_text}."

    # 🔥 INTENT: Comparison
    if "compare" in q:
        return (
            "I can compare departmental performance. Try asking: 'Compare education and health' or 'Compare spending across years'."
        )

    # FALLBACK
    return (
        f"I'm here to help with the {year} budget. You can ask about specific departments, "
        "the highest/lowest spending sectors, inflation rates, or a general summary of the year's performance."
    )
