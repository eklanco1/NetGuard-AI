import pandas as pd
import numpy as np
from pathlib import Path

# Putanja do dataseta
BASE_DIR = Path(__file__).resolve().parent.parent
DATASET_PATH = BASE_DIR / "data" / "raw" / "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"

# Ucitavanje dataseta
df = pd.read_csv(DATASET_PATH, low_memory=False)

# Uklanjanje razmaka iz naziva kolona
df.columns = df.columns.str.strip()

print("=== PROFILIRANJE DATASETA ===")

print("\nDimenzije dataseta:")
print(df.shape)

# Provjera nedostajucih vrijednosti
print("\n=== NaN VRIJEDNOSTI ===")

nan_values = df.isna().sum()
print(nan_values[nan_values > 0])

print("\nUkupan broj NaN vrijednosti:")
print(df.isna().sum().sum())

# Provjera beskonacnih vrijednosti
print("\n=== BESKONACNE VRIJEDNOSTI ===")

numeric_df = df.select_dtypes(include=[np.number])

inf_values = np.isinf(numeric_df).sum()
print(inf_values[inf_values > 0])

print("\nUkupan broj beskonacnih vrijednosti:")
print(np.isinf(numeric_df).sum().sum())

# Provjera distribucije klasa
print("\n=== DISTRIBUCIJA KLASA ===")
print(df["Label"].value_counts())

print("\n=== PROFILIRANJE ZAVRSENO ===")

# Provjera redova sa NaN i beskonacnim vrijednostima

nan_rows = df.isna().any(axis=1)

inf_rows = np.isinf(numeric_df).any(axis=1)

problematic_rows = nan_rows | inf_rows

print("\n=== PROBLEMATICNI REDOVI ===")

print("Broj redova sa NaN vrijednostima:")
print(nan_rows.sum())

print("Broj redova sa beskonacnim vrijednostima:")
print(inf_rows.sum())

print("Ukupan broj problematicnih redova:")
print(problematic_rows.sum())

print("\nKlase problematicnih redova:")
print(df.loc[problematic_rows, "Label"].value_counts())
