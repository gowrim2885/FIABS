def what_if_analysis(question: str, context: dict): 
    q = question.lower() 

    inflation = context.get("inflation", 5.0) 
    revenue = context.get("revenue", 1000000) 
    deficit = context.get("deficit", 0.0) 
    gdp = context.get("gdp", 0.0) 
    year = context.get("year", "selected year") 

    # 🔥 Inflation Simulation 
    if "inflation" in q: 
        if "increase" in q or "high" in q or "10" in q: 
            return f""" 
📊 What-If Analysis ({year}): 

If inflation rises significantly, economic impact may include: 

• Reduced purchasing power 
• Slower GDP growth 
• Increased fiscal pressure 

👉 Recommendation: 
Control inflation through monetary policies and reduce excess spending. 
""" 
        else: 
            return f""" 
📊 What-If Analysis ({year}): 

Lower inflation can stabilize the economy and improve GDP growth. 
""" 

    # 🔥 Revenue Simulation 
    if "revenue" in q: 
        return f""" 
📊 What-If Analysis ({year}): 

If government revenue increases: 

• More funds available for development 
• Reduced fiscal deficit 
• Increased investment in infrastructure 

👉 Recommendation: 
Improve tax efficiency and economic activity. 
""" 

    # 🔥 Deficit Simulation 
    if "deficit" in q: 
        return f""" 
📊 What-If Analysis ({year}): 

If fiscal deficit increases: 

• Government borrowing will rise 
• Debt burden increases 
• Long-term economic risk grows 

👉 Recommendation: 
Optimize spending and increase revenue sources. 
""" 

    return None 
