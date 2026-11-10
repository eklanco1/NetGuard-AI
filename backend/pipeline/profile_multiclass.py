
from pathlib import Path
import pandas as pd

# Putanja do multiclass dataseta
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data" / "raw" / "multiclass"

# Pronalazimo sve CSV fajlove
csv_files = sorted(DATA_DIR.glob("*.csv"))

print("=" * 60)
print("NETGUARD AI - MULTICLASS DATASET PROFILING")
print("=" * 60)

print(f"\nBroj CSV fajlova: {len(csv_files)}")

if not csv_files:
    raise FileNotFoundError(
        f"Nema CSV fajlova u folderu: {DATA_DIR}"
    )

total_rows = 0
all_labels = {}
reference_columns = None

for file in csv_files:

    print(f"\nFajl: {file.name}")

    # Citamo samo nazive kolona
    columns = pd.read_csv(file, nrows=0).columns.str.strip().tolist()

    if reference_columns is None:
        reference_columns = columns

    if columns != reference_columns:
        print("UPOZORENJE: Kolone se razlikuju!")
    else:
        print("Kolone: OK")

    if "Label" not in columns:
        print("GRESKA: Nedostaje Label kolona!")
        continue

    # Ucitavamo samo Label kolonu radi ustede memorije
    labels = pd.read_csv(
        file,
        usecols=lambda col: col.strip() == "Label",
        low_memory=False
    )

    labels.columns = labels.columns.str.strip()

    labels["Label"] = labels["Label"].astype(str).str.strip()

    counts = labels["Label"].value_counts()

    total_rows += len(labels)

    print(f"Broj zapisa: {len(labels):,}")

    for label, count in counts.items():

        all_labels[label] = all_labels.get(label, 0) + int(count)

        print(f"  {label}: {count:,}")

print("\n" + "=" * 60)
print("UKUPNA STATISTIKA")
print("=" * 60)

print(f"\nUkupno mrežnih zapisa: {total_rows:,}")

print("\nRaspodjela klasa:")

for label, count in sorted(
    all_labels.items(),
    key=lambda item: item[1],
    reverse=True
):
    percentage = count / total_rows * 100

    print(
        f"{label:30s} "
        f"{count:10,} "
        f"({percentage:.2f}%)"
    )

print(f"\nBroj razlicitih klasa: {len(all_labels)}")
