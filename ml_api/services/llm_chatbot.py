import os

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency at runtime
    OpenAI = None


def generate_llm_response(question, data, context):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or OpenAI is None:
        return "AI service is unavailable, so I am using the local fiscal dataset responses instead."

    try:
        client = OpenAI(api_key=api_key)
        data_summary = "\n".join(
            f"{row.get('department')}: budget={row.get('budget')}, spending={row.get('spending')}"
            for row in data[:8]
        )
        prompt = f"""
You are a concise fiscal assistant.
Answer using the provided dataset only.

Context year: {context.get("year")}
Available years: {context.get("available_years")}
Summary:
{data_summary}

Question: {question}
"""
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return "AI service is unavailable, so I am using the local fiscal dataset responses instead."
