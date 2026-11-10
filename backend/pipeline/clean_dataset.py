
import pandas as pd
import numpy as np
from pathlib import Path


def clean_dataset():

    # Putanje do dataseta
    BASE_DIR = Path(__file__).resolve().parent.parent

    INPUT_PATH = BASE_DIR / "data" / "raw" / "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"

    OUTPUT_PATH = BASE_DIR / "data" / "processed" / "cicids2017_ddos_clean.csv"

    # Ucitavanje originalnog dataseta
    df = pd.read_csv(INPUT_PATH, low_memory=False)

    df.columns = df.columns.str.strip()

    print("\n=== DATA CLEANING ===")

    print("\nBroj zapisa prije ciscenja:")
    print(len(df))

    # Zamjena beskonacnih vrijednosti sa NaN
    df = df.replace([np.inf, -np.inf], np.nan)

    # Uklanjanje redova sa NaN vrijednostima
    df_clean = df.dropna().copy()

    print("\nBroj zapisa nakon ciscenja:")
    print(len(df_clean))

    print("\nBroj uklonjenih redova:")
    print(len(df) - len(df_clean))

    # Provjera preostalih NaN vrijednosti
    print("\nPreostale NaN vrijednosti:")
    print(df_clean.isna().sum().sum())

    # Provjera beskonacnih vrijednosti
    numeric_df = df_clean.select_dtypes(include=[np.number])

    print("\nPreostale beskonacne vrijednosti:")
    print(np.isinf(numeric_df).sum().sum())

    # Distribucija klasa
    print("\nDistribucija klasa:")
    print(df_clean["Label"].value_counts())

    # Cuvanje ociscenog dataseta
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    df_clean.to_csv(OUTPUT_PATH, index=False)

    print("\nOcisceni dataset je sacuvan!")
    print(OUTPUT_PATH)

    print("\n=== DATA CLEANING ZAVRSEN ===")


if __name__ == "__main__":
    clean_dataset()
