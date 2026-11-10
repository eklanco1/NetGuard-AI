
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split


def check_duplicates():

    BASE_DIR = Path(__file__).resolve().parent.parent

    DATASET_PATH = (
        BASE_DIR / "data" / "processed" /
        "cicids2017_ddos_clean.csv"
    )

    # Ucitavanje ociscenog dataseta
    df = pd.read_csv(DATASET_PATH, low_memory=False)
    df.columns = df.columns.str.strip()

    print("=== PROVJERA DUPLIKATA ===")

    print("\nUkupan broj zapisa:")
    print(len(df))

    # Provjera potpuno identicnih redova
    duplicates = df.duplicated().sum()

    print("\nBroj dodatnih identicnih redova:")
    print(duplicates)

    # Provjera duplikata bez Label kolone
    X = df.drop(columns=["Label"])

    feature_duplicates = X.duplicated().sum()

    print("\nBroj dodatnih redova sa istim features:")
    print(feature_duplicates)

    # Kreiranje otisaka ulaznih karakteristika
    feature_hashes = pd.util.hash_pandas_object(
        X, index=False
    )

    # Provjera istih karakteristika sa razlicitim klasama
    label_counts = df.groupby(feature_hashes)["Label"].nunique()

    conflicting = (label_counts > 1).sum()

    print("\nBroj razlicitih zapisa sa konfliktnim Label:")
    print(conflicting)

    # Ista podjela kao u prepare_dataset.py
    train_idx, test_idx = train_test_split(
        df.index,
        test_size=0.2,
        random_state=42,
        stratify=df["Label"]
    )

    train_hashes = set(feature_hashes.loc[train_idx])

    overlap = feature_hashes.loc[test_idx].isin(
        train_hashes
    ).sum()

    print("\n=== PROVJERA PREKLAPANJA ===")

    print("Testnih redova sa istim features u treningu:")
    print(overlap)

    print("\n=== PROVJERA ZAVRSENA ===")


if __name__ == "__main__":
    check_duplicates()
