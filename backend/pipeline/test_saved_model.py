
import joblib
import pandas as pd
from pathlib import Path


def test_saved_model():

    BASE_DIR = Path(__file__).resolve().parent.parent

    MODEL_PATH = BASE_DIR / "models" / "netguard_mlp.joblib"

    DATASET_PATH = (
        BASE_DIR / "data" / "processed" /
        "cicids2017_ddos_clean.csv"
    )

    print("=== TESTIRANJE SACUVANOG MODELA ===")

    # Ucitavanje sacuvanog modela
    package = joblib.load(MODEL_PATH)

    model = package["model"]
    scaler = package["scaler"]
    feature_columns = package["feature_columns"]

    print("\nModel uspjesno ucitan!")

    # Ucitavanje podataka za provjeru
    df = pd.read_csv(DATASET_PATH, low_memory=False)
    df.columns = df.columns.str.strip()

    labels = {
        0: "BENIGN",
        1: "DDoS"
    }

    # Testiranje jednog BENIGN i jednog DDoS zapisa
    for actual_label in ["BENIGN", "DDoS"]:

        sample = df[df["Label"] == actual_label].head(1)

        if sample.empty:
            raise ValueError(
                f"Nema zapisa za klasu {actual_label}"
            )

        # Izdvajanje karakteristika
        X_sample = sample[feature_columns]

        # Standardizacija sacuvanim scalerom
        X_scaled = scaler.transform(X_sample)

        # Predikcija sacuvanim modelom
        prediction = int(model.predict(X_scaled)[0])

        # Procjena vjerovatnoce DDoS klase
        probabilities = model.predict_proba(X_scaled)[0]

        ddos_index = list(model.classes_).index(1)
        ddos_probability = probabilities[ddos_index] * 100

        print("\n-------------------------")
        print("Stvarna klasa:", actual_label)
        print("Predikcija modela:", labels[prediction])
        print(
            f"Procijenjena vjerovatnoca DDoS: "
            f"{ddos_probability:.2f}%"
        )

    print("\n=== TESTIRANJE ZAVRSENO ===")


if __name__ == "__main__":
    test_saved_model()
