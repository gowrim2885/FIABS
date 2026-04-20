import os

from .dataset_loader import load_dataset, yearly_summary


PROCESSED_DATA_PATH = "data/uploads/processed_data.csv"


def process_data():
    try:
        df = load_dataset()
    except Exception:
        return "Error: Raw data not found"

    df_grouped = yearly_summary(df)
    os.makedirs(os.path.dirname(PROCESSED_DATA_PATH), exist_ok=True)
    df_grouped.to_csv(PROCESSED_DATA_PATH, index=False)
    return "Data processed successfully"
