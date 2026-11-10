
from pathlib import Path
import pandas as pd

# Putanja do naseg dataseta
DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
)

# Ucitavamo prvih 1000 redova
df = pd.read_csv(DATA_PATH, nrows=1000)

# Uklanjamo razmake iz naziva kolona
df.columns = df.columns.str.strip()

# Prikaz broja redova i kolona
print("Dimenzije dataseta:", df.shape)

# Prikaz naziva svih kolona
print("\nNazivi kolona:")
print(df.columns.tolist())

# Prikaz prvih 5 zapisa
print("\nPrvih 5 zapisa:")
print(df.head())

# Prikaz broja zapisa po vrsti saobracaja
print("\nVrste mreznog saobracaja:")
print(df["Label"].value_counts())


# Brojimo oznake u cijelom datasetu

print("\nAnaliza svih oznaka u datasetu:")

label_counts = {}

for chunk in pd.read_csv(
    DATA_PATH,
    usecols=lambda col: col.strip() == "Label",
    chunksize=50000
):
    chunk.columns = chunk.columns.str.strip()

    counts = chunk["Label"].value_counts()

    for label, count in counts.items():
        label = label.strip()

        label_counts[label] = (
            label_counts.get(label, 0) + count
        )

print("\nUkupan broj zapisa po klasama:")

for label, count in label_counts.items():
    print(f"{label}: {count}")

print("\nUkupno zapisa:", sum(label_counts.values()))
