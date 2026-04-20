import joblib 
import numpy as np 
import os

MODEL_PATH = "models/gdp_model.pkl" 

def predict_gdp(revenue, inflation): 
    if not os.path.exists(MODEL_PATH):
        return "Error: Model not trained. Please train the model first."

    model = joblib.load(MODEL_PATH) 

    prediction = model.predict([[revenue, inflation]]) 

    return float(prediction[0]) 
