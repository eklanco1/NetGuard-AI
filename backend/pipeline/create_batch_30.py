
import pandas as pd
from pathlib import Path


def create_batch_30():

    BASE_DIR = Path(__file__).resolve().parent.parent

    INPUT_PATH = (
        BASE_DIR / "data" / "processed" /
        "cicids2017_ddos_clean.csv"
    )

    OUTPUT_PATH = BASE_DIR / "data" / "test_batch_30.csv"

    # Ucitavanje ociscenog dataseta
    df = pd.read_csv(INPUT_PATH, low_memory=False)

    df.columns = df.columns.str.strip()

    # Uklanjanje duplikata
    df = df.drop_duplicates()

    # Izdvajanje 15 zapisa iz svake klase
    benign = df[df["Label"] == "BENIGN"].head(15)

    ddos = df[df["Label"] == "DDoS"].head(15)

    # Spajanje u jedan dataset
    batch = pd.concat([benign, ddos], ignore_index=True)

    # Mijesanje redoslijeda zapisa
    batch = batch.sample(
        frac=1,
        random_state=42
    ).reset_index(drop=True)

    # Cuvanje CSV fajla
    batch.to_csv(OUTPUT_PATH, index=False)

    print("=== BATCH TEST - 30 ZAPISA ===")
    print("Broj zapisa:", len(batch))
    print("Broj kolona:", len(batch.columns))

    print("\nKlase:")
    print(batch["Label"].value_counts())

    print("\nFajl:", OUTPUT_PATH)


if __name__ == "__main__":
    create_batch_30()
