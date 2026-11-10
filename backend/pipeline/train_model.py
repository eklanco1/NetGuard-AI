
import numpy as np
from copy import deepcopy
import joblib
from pathlib import Path

from sklearn.neural_network import MLPClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    log_loss
)

from pipeline.prepare_dataset import prepare_dataset


def train_model():

    print("=== TRENIRANJE NETGUARD AI MODELA ===")

    # Ucitavanje pripremljenih podataka
    (
        X_train,
        X_val,
        X_test,
        y_train,
        y_val,
        y_test,
        scaler
    ) = prepare_dataset()

    # Kreiranje neuronske mreze
    model = MLPClassifier(
        hidden_layer_sizes=(64, 32),
        activation="relu",
        solver="adam",
        batch_size=512,
        random_state=42,
        early_stopping=False
    )

    # Parametri treniranja
    max_epochs = 30
    patience = 5

    best_val_loss = float("inf")
    best_model = None
    epochs_without_improvement = 0

    print("\n=== POCETAK TRENIRANJA ===")

    for epoch in range(max_epochs):

        # Treniranje jedne epohe
        if epoch == 0:
            model.partial_fit(
                X_train,
                y_train,
                classes=np.array([0, 1])
            )
        else:
            model.partial_fit(X_train, y_train)

        # Predikcije na validacijskom skupu
        val_pred = model.predict(X_val)
        val_proba = model.predict_proba(X_val)

        # Validacijske metrike
        val_accuracy = accuracy_score(y_val, val_pred)

        val_loss = log_loss(
            y_val,
            val_proba,
            labels=[0, 1]
        )

        print(
            f"Epoch {epoch + 1}/{max_epochs} | "
            f"Train loss: {model.loss_:.6f} | "
            f"Val loss: {val_loss:.6f} | "
            f"Val accuracy: {val_accuracy:.4f}"
        )

        # Pracenje najboljeg modela
        if val_loss < best_val_loss:

            best_val_loss = val_loss
            best_model = deepcopy(model)
            epochs_without_improvement = 0

        else:
            epochs_without_improvement += 1

        # Zaustavljanje ako nema poboljsanja
        if epochs_without_improvement >= patience:

            print("\nEarly stopping aktiviran!")
            break

    # Vracanje najboljeg modela
    model = best_model

    print("\n=== TRENIRANJE ZAVRSENO ===")

    # Konacno testiranje
    y_pred = model.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)

    print("\n=== REZULTATI MODELA ===")

    print("\nAccuracy:")
    print(round(accuracy * 100, 2), "%")

    print("\nClassification Report:")
    print(classification_report(
        y_test,
        y_pred,
        target_names=["BENIGN", "DDoS"],
        digits=4
    ))

    print("\nConfusion Matrix:")
    print(confusion_matrix(y_test, y_pred))

    
    # Cuvanje treniranog modela i scalera
    print("\n=== CUVANJE MODELA ===")

    BASE_DIR = Path(__file__).resolve().parent.parent

    MODEL_PATH = BASE_DIR / "models" / "netguard_mlp.joblib"

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Paket sa svim potrebnim podacima
    model_package = {
        "model": model,
        "scaler": scaler,
        "feature_columns": scaler.feature_names_in_.tolist(),
        "label_mapping": {
            "BENIGN": 0,
            "DDoS": 1
        }
    }

    joblib.dump(model_package, MODEL_PATH)

    print("Model uspjesno sacuvan!")
    print("Lokacija:", MODEL_PATH)



if __name__ == "__main__":
    train_model()
