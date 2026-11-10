
import pandas as pd
from pathlib import Path


def create_batch_sample():

    BASE_DIR = Path(__file__).resolve().parent.parent

    INPUT_PATH = (
        BASE_DIR / "data" / "processed" /
        "cicids2017_ddos_clean.csv"
    )

    OUTPUT_PATH = (
        BASE_DIR / "data" / "test_batch.csv"
    )

    # Ucitavanje stvarnog dataseta
    df = pd.read_csv(INPUT_PATH, low_memory=False)

    # Uklanjanje razmaka iz naziva kolona
    df.columns = df.columns.str.strip()

    # Uklanjanje duplikata
    df = df.drop_duplicates()

    # Uzimamo 5 BENIGN i 5 DDoS zapisa
    benign = df[df["Label"] == "BENIGN"].head(5)
    ddos = df[df["Label"] == "DDoS"].head(5)

    # Spajanje zapisa
    batch = pd.concat([benign, ddos])

    # Cuvanje CSV fajla
    batch.to_csv(OUTPUT_PATH, index=False)

    print("=== BATCH TESTNI UZORAK ===")
    print("Broj zapisa:", len(batch))
    print("Broj kolona:", len(batch.columns))
    print("Klase:")
    print(batch["Label"].value_counts())
    print("Fajl:", OUTPUT_PATH)


if __name__ == "__main__":
    create_batch_sample()
