
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


def prepare_dataset():

    # Putanja do ociscenog dataseta
    BASE_DIR = Path(__file__).resolve().parent.parent

    DATASET_PATH = (
        BASE_DIR / "data" / "processed" /
        "cicids2017_ddos_clean.csv"
    )

    # Ucitavanje dataseta
    df = pd.read_csv(DATASET_PATH, low_memory=False)
    df.columns = df.columns.str.strip()

    # Uklanjanje duplikata
    print("\n=== UKLANJANJE DUPLIKATA ===")

    print("Broj zapisa prije:", len(df))

    df = df.drop_duplicates().copy()

    print("Broj zapisa poslije:", len(df))

    print("\n=== PRIPREMA DATASETA ===")

    # Ulazne karakteristike
    X = df.drop(columns=["Label"])

    # Ciljna varijabla
    y = df["Label"].map({
        "BENIGN": 0,
        "DDoS": 1
    })

    if y.isna().any():
        raise ValueError("Nepoznate oznake klasa!")

    non_numeric = X.select_dtypes(
        exclude="number"
    ).columns

    if len(non_numeric) > 0:
        raise ValueError(
            f"Nenumericke kolone: {list(non_numeric)}"
        )

    print("Ukupan broj zapisa:", len(df))
    print("Broj karakteristika:", X.shape[1])

    # Prva podjela: 80% trening + 20% test
    X_train_full, X_test, y_train_full, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42,
            stratify=y
        )
    )

    # Druga podjela:
    # Od 80% izdvajamo 10% za validaciju
    X_train, X_val, y_train, y_val = (
        train_test_split(
            X_train_full,
            y_train_full,
            test_size=0.1,
            random_state=42,
            stratify=y_train_full
        )
    )

    print("\n=== PODJELA PODATAKA ===")

    print("Trening:", X_train.shape)
    print("Validacija:", X_val.shape)
    print("Test:", X_test.shape)

    print("\n=== STANDARDIZACIJA ===")

    scaler = StandardScaler()

    # Scaler uci samo na trening podacima
    X_train_scaled = scaler.fit_transform(X_train)

    # Validacija koristi naucena pravila
    X_val_scaled = scaler.transform(X_val)

    # Test koristi ista naucena pravila
    X_test_scaled = scaler.transform(X_test)

    print("Standardizacija uspjesno zavrsena!")

    print("\n=== PRIPREMA ZAVRSENA ===")

    return (
        X_train_scaled,
        X_val_scaled,
        X_test_scaled,
        y_train,
        y_val,
        y_test,
        scaler
    )


if __name__ == "__main__":
    prepare_dataset()
