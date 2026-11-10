
import json
import joblib
import pandas as pd
from pathlib import Path


def generate_test_request():

    BASE_DIR = Path(__file__).resolve().parent.parent

    DATASET_PATH = (
        BASE_DIR / "data" / "processed" /
        "cicids2017_ddos_clean.csv"
    )

    MODEL_PATH = (
        BASE_DIR / "models" / "netguard_mlp.joblib"
    )

    OUTPUT_PATH = (
        BASE_DIR / "data" / "test_requests" /
        "ddos_request.json"
    )

    print("=== GENERISANJE TESTNOG ZAHTJEVA ===")

    # Ucitavanje dataseta
    df = pd.read_csv(DATASET_PATH, low_memory=False)
    df.columns = df.columns.str.strip()

    # Ucitavanje redoslijeda karakteristika
    package = joblib.load(MODEL_PATH)
    feature_columns = package["feature_columns"]

    # Uzimamo jedan BENIGN zapis
    sample = df[df["Label"] == "DDoS"].iloc[0]

    # Kreiranje JSON zahtjeva
    features = {
        name: float(sample[name])
        for name in feature_columns
    }

    request_data = {
        "features": features
    }

    # Cuvanje JSON fajla
    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(
            request_data,
            f,
            indent=4,
            allow_nan=False
        )

    print("\nJSON zahtjev uspjesno kreiran!")
    print("Broj karakteristika:", len(features))
    print("Stvarna klasa: DDoS")
    print("Lokacija:", OUTPUT_PATH)


if __name__ == "__main__":
    generate_test_request()
