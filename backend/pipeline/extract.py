
import csv
from pathlib import Path

DATA_PATH = (
    Path(__file__).resolve().parents[1]
    / "data"
    / "raw"
    / "traffic_sample.csv"
)


def extract_data():
    with open(DATA_PATH, mode="r", encoding="utf-8", newline="") as file:
        reader = csv.DictReader(file)
        records = list(reader)

    return records


if __name__ == "__main__":
    data = extract_data()

    print("Broj učitanih zapisa:", len(data))
    print("Prvi zapis:", data[0])
