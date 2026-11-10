
import json
from pathlib import Path

import joblib
import pandas as pd


def create_test_sample():

    # Glavni backend folder
    BASE_DIR = Path(__file__).resolve().parent.parent

    # Putanja do ociscenog dataseta
    DATASET_PATH = (
        BASE_DIR / "data" / "processed" /
        "cicids2017_ddos_clean.csv"
    )

    # Putanja do sacuvanog AI modela
    MODEL_PATH = (
        BASE_DIR / "models" / "netguard_mlp.joblib"
    )

    # Ucitavanje modela i redoslijeda karakteristika
    package = joblib.load(MODEL_PATH)
    feature_columns = package["feature_columns"]

    # Ucitavanje dataseta
    df = pd.read_csv(DATASET_PATH, low_memory=False)
    df.columns = df.columns.str.strip()

    # Uklanjanje duplikata, kao kod pripreme
    df = df.drop_duplicates().copy()

    # Uzimamo prvi stvarni zapis
    sample = df.iloc[0]

    # Izdvajanje 78 karakteristika
    features = {
        name: float(sample[name])
        for name in feature_columns
    }

    # JSON format koji ocekuje FastAPI
    request_data = {
        "features": features
    }

    # Cuvanje JSON fajla
    OUTPUT_PATH = BASE_DIR / "data" / "test_sample.json"

    with open(OUTPUT_PATH, "w", encoding="utf-8") as file:
        json.dump(request_data, file, indent=4)

    print("=== TESTNI UZORAK KREIRAN ===")
    print("Broj karakteristika:", len(features))
    print("Originalna klasa:", sample["Label"])
    print("JSON fajl:", OUTPUT_PATH)


if __name__ == "__main__":
    create_test_sample()
