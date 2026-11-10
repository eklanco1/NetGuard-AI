
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
INPUT_DIR = BASE_DIR / "data" / "raw" / "multiclass"
OUTPUT_DIR = BASE_DIR / "data" / "processed"
OUTPUT_FILE = OUTPUT_DIR / "multiclass_sample.csv"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Brojevi dobijeni profiliranjem dataseta
CLASS_COUNTS = {
    "BENIGN": 2273097,
    "DoS": 252661,
    "PortScan": 158930,
    "DDoS": 128027,
    "Brute Force": 13835,
    "Web Attack": 2180,
    "Bot": 1966
}

# Maksimalni ciljani broj redova za velike klase
TARGET = 100000

SAMPLE_RATES = {
    label: min(1.0, TARGET / count)
    for label, count in CLASS_COUNTS.items()
}


def normalize_label(label):
    label = str(label).strip()

    if label in ("BENIGN", "DDoS", "PortScan", "Bot"):
        return label

    if label.startswith("DoS "):
        return "DoS"

    if label in ("FTP-Patator", "SSH-Patator"):
        return "Brute Force"

    if label.startswith("Web Attack"):
        return "Web Attack"

    # Infiltration, Heartbleed i nepoznate klase
    return None


def prepare_dataset():
    files = sorted(INPUT_DIR.glob("*.csv"))

    if len(files) != 8:
        raise ValueError(
            f"Ocekivano 8 CSV fajlova, pronadjeno {len(files)}"
        )

    if OUTPUT_FILE.exists():
        OUTPUT_FILE.unlink()

    first_write = True
    total_saved = 0
    random_state = 42

    for file in files:
        print(f"\nObradjujem: {file.name}")

        file_saved = 0

        for chunk in pd.read_csv(
            file,
            chunksize=20000,
            low_memory=False
        ):
            chunk.columns = chunk.columns.str.strip()

            if "Label" not in chunk.columns:
                raise ValueError(
                    f"Nedostaje Label kolona: {file.name}"
                )

            chunk["Label"] = (
                chunk["Label"].map(normalize_label)
            )

            # Uklanjamo klase koje nismo odabrali
            chunk = chunk.dropna(subset=["Label"])

            selected_chunks = []

            for label, group in chunk.groupby("Label"):
                rate = SAMPLE_RATES[label]

                sampled = group.sample(
                    frac=rate,
                    random_state=random_state
                )

                selected_chunks.append(sampled)

            if not selected_chunks:
                continue

            selected = pd.concat(
                selected_chunks,
                ignore_index=True
            )

            selected.to_csv(
                OUTPUT_FILE,
                mode="w" if first_write else "a",
                header=first_write,
                index=False
            )

            first_write = False
            file_saved += len(selected)
            total_saved += len(selected)

            random_state += 1

        print(f"Sacuvano zapisa: {file_saved:,}")

    print("\n" + "=" * 60)
    print("MULTICLASS SAMPLING COMPLETED")
    print("=" * 60)

    print(f"Ukupno sacuvano: {total_saved:,}")
    print(f"Lokacija: {OUTPUT_FILE}")


if __name__ == "__main__":
    prepare_dataset()
