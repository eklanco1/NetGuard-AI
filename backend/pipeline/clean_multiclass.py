
from pathlib import Path
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_FILE = (
    BASE_DIR / "data" / "processed" / "multiclass_sample.csv"
)

OUTPUT_DIR = BASE_DIR / "data" / "processed" / "multiclass"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

RANDOM_STATE = 42


def clean_and_split():

    print("=" * 60)
    print("NETGUARD AI - MULTICLASS CLEANING")
    print("=" * 60)

    # 1. Ucitavanje dataseta
    df = pd.read_csv(INPUT_FILE, low_memory=False)

    df.columns = df.columns.str.strip()

    # Uklanjamo eventualne dodatne indeksne kolone
    df = df.loc[
        :,
        ~df.columns.str.startswith("Unnamed:")
    ]

    print(f"\nPocetni broj zapisa: {len(df):,}")
    print(f"Broj kolona: {len(df.columns)}")

    if "Label" not in df.columns:
        raise ValueError("Nedostaje Label kolona!")

    if df.columns.duplicated().any():
        raise ValueError("Postoje duplirani nazivi kolona!")

    # 2. Odvajamo ulazne karakteristike
    feature_columns = [
        col for col in df.columns if col != "Label"
    ]

    print(
        f"Broj ulaznih karakteristika: "
        f"{len(feature_columns)}"
    )

    if len(feature_columns) != 78:
        raise ValueError(
            "Ocekivano je 78 ulaznih karakteristika!"
        )

    # 3. Pretvaranje svih karakteristika u brojeve
    for column in feature_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # 4. Uklanjanje NaN i Infinity vrijednosti
    df[feature_columns] = df[feature_columns].replace(
        [np.inf, -np.inf],
        np.nan
    )

    invalid_rows = df[feature_columns].isna().any(axis=1)

    print(
        f"\nNeispravni zapisi: "
        f"{invalid_rows.sum():,}"
    )

    df = df.loc[~invalid_rows].copy()

    # 5. Uklanjanje duplikata
    before_duplicates = len(df)

    df = df.drop_duplicates(
        subset=feature_columns + ["Label"]
    ).copy()

    removed_duplicates = before_duplicates - len(df)

    print(
        f"Uklonjeni duplikati: "
        f"{removed_duplicates:,}"
    )

    # 6. Provjera konfliktnih oznaka
    # Iste karakteristike ne smiju imati
    # razlicite oznake u nasem skupu.

    feature_hash = pd.util.hash_pandas_object(
        df[feature_columns],
        index=False
    )

    temp = pd.DataFrame({
        "hash": feature_hash.to_numpy(),
        "label": df["Label"].to_numpy()
    })

    conflicting_hashes = temp.groupby(
        "hash"
    )["label"].nunique()

    conflicting_hashes = conflicting_hashes[
        conflicting_hashes > 1
    ].index

    conflicting_rows = feature_hash.isin(
        conflicting_hashes
    )

    print(
        f"Zapisi s konfliktnim oznakama: "
        f"{conflicting_rows.sum():,}"
    )

    df = df.loc[~conflicting_rows].copy()

    # 7. Raspodjela klasa
    print("\nRaspodjela klasa nakon ciscenja:")

    print(df["Label"].value_counts())

    if df["Label"].nunique() != 7:
        raise ValueError(
            "Nakon ciscenja nije ostalo svih 7 klasa!"
        )

    # 8. Podjela na trening i test
    train_val, test = train_test_split(
        df,
        test_size=0.20,
        random_state=RANDOM_STATE,
        stratify=df["Label"]
    )

    # 9. Podjela na trening i validaciju
    # 12.5% od preostalih 80% = 10% ukupno
    train, val = train_test_split(
        train_val,
        test_size=0.125,
        random_state=RANDOM_STATE,
        stratify=train_val["Label"]
    )

    # 10. Cuvanje
    train.to_csv(
        OUTPUT_DIR / "train.csv",
        index=False
    )

    val.to_csv(
        OUTPUT_DIR / "val.csv",
        index=False
    )

    test.to_csv(
        OUTPUT_DIR / "test.csv",
        index=False
    )

    print("\n" + "=" * 60)
    print("MULTICLASS DATASET READY")
    print("=" * 60)

    print(f"Train: {len(train):,}")
    print(f"Validation: {len(val):,}")
    print(f"Test: {len(test):,}")

    print("\nFajlovi sacuvani u:")
    print(OUTPUT_DIR)

    print("\nRaspodjela klasa - TRAIN:")
    print(train["Label"].value_counts())


if __name__ == "__main__":
    clean_and_split()
