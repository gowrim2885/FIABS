from sklearn.ensemble import IsolationForest 
import pandas as pd 
import os

DATA_PATH = "data/uploads/analyst_data.csv"

def detect_anomalies(): 
    if not os.path.exists(DATA_PATH):
        return []

    df = pd.read_csv(DATA_PATH) 

    model = IsolationForest(contamination=0.1, random_state=42) 
    df["anomaly"] = model.fit_predict(df[["revenue", "inflation", "gdp"]]) 

    anomalies = df[df["anomaly"] == -1] 

    return anomalies.to_dict(orient="records") 
