
from pathlib import Path
from typing import Literal
import logging

import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from pipeline.predict_api import load_model

router = APIRouter()
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
SAMPLES_DIR = BASE_DIR / "data" / "test_requests"


class MonitoringResult(BaseModel):
    sample_type: str
    prediction: str
    ddos_probability_percent: float
    packets_per_second: float
    simulated: bool = True


@router.get("/monitoring/sample", response_model=MonitoringResult)
def analyze_monitoring_sample(
    scenario: Literal["BENIGN", "DDoS"] = Query(default="BENIGN")
):
    # Odabir simuliranog mrežnog uzorka
    filename = (
        "ddos_request.json"
        if scenario == "DDoS"
        else "benign_request.json"
    )

    sample_path = SAMPLES_DIR / filename

    try:
        import json

        with sample_path.open("r", encoding="utf-8") as file:
            sample = json.load(file)

        # Podržava JSON oblika {"features": {...}}
        # ili direktni rječnik karakteristika
        features = sample.get("features", sample)

        if not isinstance(features, dict):
            raise ValueError("Invalid sample structure")

        package = load_model()

        model = package["model"]
        scaler = package["scaler"]
        feature_columns = package["feature_columns"]

        expected = set(feature_columns)
        received = set(features.keys())

        if expected != received:
            raise ValueError(
                "Sample features do not match the trained model"
            )

        X = pd.DataFrame([{
            name: features[name]
            for name in feature_columns
        }])

        if not np.isfinite(X.to_numpy(dtype=float)).all():
            raise ValueError("Sample contains invalid numerical values")

        X_scaled = scaler.transform(X)

        prediction = int(model.predict(X_scaled)[0])
        probabilities = model.predict_proba(X_scaled)[0]

        ddos_index = list(model.classes_).index(1)
        ddos_probability = float(probabilities[ddos_index] * 100)

        # CIC-IDS2017 Flow Packets/s karakteristika
        packets_per_second = float(
            features.get("Flow Packets/s", 0)
        )

        return MonitoringResult(
            sample_type=scenario,
            prediction="DDoS" if prediction == 1 else "BENIGN",
            ddos_probability_percent=round(ddos_probability, 2),
            packets_per_second=round(packets_per_second, 2),
        )

    except (OSError, ValueError, TypeError, KeyError) as exc:
        logger.exception("Monitoring sample could not be processed")
        raise HTTPException(
            status_code=500,
            detail="Monitoring sample configuration is invalid."
        ) from exc
    except Exception as exc:
        logger.exception("Monitoring inference failed")
        raise HTTPException(
            status_code=500,
            detail="Monitoring inference failed."
        ) from exc
