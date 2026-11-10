
import os
import logging
from pathlib import Path
from functools import lru_cache

import joblib
import numpy as np
import pandas as pd
import psycopg

from psycopg.types.json import Jsonb
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent

# Ucitavanje konfiguracije baze
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger(__name__)

router = APIRouter()


# Struktura ulaznih podataka
class TrafficInput(BaseModel):
    features: dict[str, float]


# Ucitavanje sacuvanog AI modela
@lru_cache(maxsize=1)
def load_model():

    MODEL_PATH = (
        BASE_DIR / "models" / "netguard_mlp.joblib"
    )

    return joblib.load(MODEL_PATH)


# API endpoint za AI predikciju
@router.post("/predict")
def predict_traffic(data: TrafficInput):

    package = load_model()

    model = package["model"]
    scaler = package["scaler"]
    feature_columns = package["feature_columns"]

    # Provjera karakteristika
    expected = set(feature_columns)
    received = set(data.features.keys())

    if expected != received:
        raise HTTPException(
            status_code=422,
            detail={
                "missing_features": sorted(expected - received),
                "extra_features": sorted(received - expected)
            }
        )

    # Priprema podataka pravilnim redoslijedom
    X = pd.DataFrame([
        {
            name: data.features[name]
            for name in feature_columns
        }
    ])

    # Provjera neispravnih numerickih vrijednosti
    if not np.isfinite(X.to_numpy()).all():
        raise HTTPException(
            status_code=422,
            detail="Podaci sadrze NaN ili beskonacne vrijednosti."
        )

    # Standardizacija
    X_scaled = scaler.transform(X)

    # AI predikcija
    prediction = int(model.predict(X_scaled)[0])

    # Procijenjena vjerovatnoca DDoS klase
    probabilities = model.predict_proba(X_scaled)[0]

    ddos_index = list(model.classes_).index(1)

    ddos_probability = float(
        probabilities[ddos_index] * 100
    )

    prediction_label = (
        "DDoS" if prediction == 1 else "BENIGN"
    )

    # CUVANJE PREDIKCIJE U POSTGRESQL
    try:
        with psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            connect_timeout=5
        ) as connection:

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    INSERT INTO ai_prediction_history (
                        prediction,
                        ddos_probability_percent,
                        features
                    )
                    VALUES (%s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        prediction_label,
                        ddos_probability,
                        Jsonb(data.features)
                    )
                )

                prediction_id = cursor.fetchone()[0]

    except psycopg.Error:
        logger.exception(
            "Greska prilikom cuvanja AI predikcije"
        )
        raise HTTPException(
            status_code=503,
            detail="Predikcija nije sacuvana. Baza nije dostupna."
        )

    # Odgovor korisniku
    return {
        "prediction_id": prediction_id,
        "prediction": prediction_label,
        "ddos_probability_percent": round(
            ddos_probability, 2
        )
    }


# API endpoint za pregled historije AI predikcija
@router.get("/predictions")
def get_predictions(
    limit: int = Query(default=20, ge=1, le=100),
    prediction: str | None = Query(default=None)
):

    print("=== UCITAVANJE HISTORIJE PREDIKCIJA ===")

    # Provjera ispravnosti filtera
    if prediction is not None:
        prediction = prediction.upper()

        if prediction not in ["BENIGN", "DDOS"]:
            raise HTTPException(
                status_code=400,
                detail="Filter mora biti BENIGN ili DDoS."
            )

        if prediction == "DDOS":
            prediction = "DDoS"

    try:
        # Povezivanje s PostgreSQL bazom
        with psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            connect_timeout=5
        ) as connection:

            with connection.cursor() as cursor:

                # Citanje posljednjih AI predikcija
                cursor.execute("""
                    SELECT
                        id,
                        prediction,
                        ddos_probability_percent,
                        created_at
                    FROM public.ai_prediction_history
                    WHERE (%s::text IS NULL OR prediction = %s)
                    ORDER BY id DESC 
                    LIMIT %s; 
                    """, (prediction, prediction, limit))

                   

                rows = cursor.fetchall()

    except psycopg.Error:
        logger.exception(
            "Greska prilikom citanja historije"
        )

        raise HTTPException(
            status_code=503,
            detail="Nije moguce ucitati historiju predikcija."
        )

    # Priprema rezultata za JSON odgovor
    predictions = []

    for row in rows:
        predictions.append({
            "id": row[0],
            "prediction": row[1],
            "ddos_probability_percent": round(row[2], 2),
            "created_at": row[3]
        })

    return {
        "count": len(predictions),
        "predictions": predictions
    }



# API endpoint za statistiku AI predikcija
@router.get("/predictions/stats")
def get_prediction_stats():

    print("=== STATISTIKA AI PREDIKCIJA ===")

    try:
        # Povezivanje s PostgreSQL bazom
        with psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            connect_timeout=5
        ) as connection:

            with connection.cursor() as cursor:

                # Racunanje statistike iz baze
                cursor.execute("""
                    SELECT
                        COUNT(*) AS total,

                        COUNT(*) FILTER (
                            WHERE prediction = 'BENIGN'
                        ) AS benign_count,

                        COUNT(*) FILTER (
                            WHERE prediction = 'DDoS'
                        ) AS ddos_count

                    FROM public.ai_prediction_history;
                """)

                result = cursor.fetchone()

    except psycopg.Error:
        logger.exception(
            "Greska prilikom ucitavanja statistike"
        )

        raise HTTPException(
            status_code=503,
            detail="Nije moguce ucitati statistiku."
        )

    total = result[0]
    benign_count = result[1]
    ddos_count = result[2]

    # Procenat DDoS predikcija
    ddos_percentage = (
        (ddos_count / total) * 100
        if total > 0 else 0
    )

    return {
        "total_predictions": total,
        "benign_predictions": benign_count,
        "ddos_predictions": ddos_count,
        "ddos_percentage": round(ddos_percentage, 2)
    }


@router.get("/predictions/timeline")

@router.get("/predictions/timeline")
def get_predictions_timeline():

    print("=== HISTORIJA AI PREDIKCIJA PO VREMENU ===")

    try:
        # Povezivanje s PostgreSQL bazom
        with psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            connect_timeout=5
        ) as connection:

            with connection.cursor() as cursor:

                # Grupisanje predikcija po satima
                cursor.execute("""
                    SELECT
                        DATE_TRUNC('hour', created_at) AS hour,

                        COUNT(*) FILTER (
                            WHERE prediction = 'BENIGN'
                        ) AS benign_count,

                        COUNT(*) FILTER (
                            WHERE prediction = 'DDoS'
                        ) AS ddos_count,

                        COUNT(*) AS total_count

                    FROM public.ai_prediction_history

                    GROUP BY DATE_TRUNC('hour', created_at)
                    ORDER BY hour ASC;
                """)

                rows = cursor.fetchall()

    except psycopg.Error:
        logger.exception(
            "Greska prilikom ucitavanja timeline statistike"
        )

        raise HTTPException(
            status_code=503,
            detail="Nije moguce ucitati timeline statistiku."
        )

    # Pretvaranje rezultata u JSON format
    timeline = []

    for row in rows:
        timeline.append({
            "hour": row[0].isoformat(),
            "benign_count": row[1],
            "ddos_count": row[2],
            "total_count": row[3]
        })

    return {
        "timeline": timeline
    }
