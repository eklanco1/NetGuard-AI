
from io import BytesIO

import os
import logging
import psycopg

logger = logging.getLogger(__name__)


import numpy as np
import pandas as pd

from fastapi import APIRouter, UploadFile, File, HTTPException

from pipeline.predict_api import load_model


router = APIRouter()


@router.post("/predict/batch")
async def predict_batch(file: UploadFile = File(...)):

    # Provjera ekstenzije fajla
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(
            status_code=400,
            detail="Dozvoljeni su samo CSV fajlovi."
        )

    # Ucitavanje CSV fajla
    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="CSV fajl je prazan."
        )

    try:
        df = pd.read_csv(BytesIO(content), low_memory=False)
    except (pd.errors.ParserError, UnicodeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Nije moguce procitati CSV fajl."
        )

    df.columns = df.columns.str.strip()

    if df.empty:
        raise HTTPException(
            status_code=400,
            detail="CSV ne sadrzi podatke."
        )

    # Ucitavanje sacuvanog AI modela
    package = load_model()

    model = package["model"]
    scaler = package["scaler"]
    feature_columns = package["feature_columns"]

    # Label je opcionalna kolona
    input_columns = set(df.columns) - {"Label"}
    expected_columns = set(feature_columns)

    if input_columns != expected_columns:
        raise HTTPException(
            status_code=422,
            detail={
                "missing_features": sorted(
                    expected_columns - input_columns
                ),
                "extra_features": sorted(
                    input_columns - expected_columns
                )
            }
        )

    # Izdvajanje karakteristika pravim redoslijedom
    X = df[feature_columns].copy()

    # Provjera numerickih vrijednosti
    try:
        X = X.apply(pd.to_numeric, errors="raise")
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail="Sve karakteristike moraju biti numericke."
        )

    if not np.isfinite(X.to_numpy(dtype=float)).all():
        raise HTTPException(
            status_code=422,
            detail="CSV sadrzi NaN ili beskonacne vrijednosti."
        )

    # Standardizacija pomocu sacuvanog scalera
    X_scaled = scaler.transform(X)

    # AI klasifikacija svih zapisa
    predictions = model.predict(X_scaled)

    # Vjerovatnoce za DDoS klasu
    probabilities = model.predict_proba(X_scaled)

    ddos_index = list(model.classes_).index(1)

    ddos_probabilities = probabilities[:, ddos_index] * 100

    # Priprema pojedinacnih rezultata
    results = []

    for i, prediction in enumerate(predictions):
        results.append({
            "row": i + 1,
            "prediction": (
                "DDoS" if int(prediction) == 1 else "BENIGN"
            ),
            "ddos_probability_percent": round(
                float(ddos_probabilities[i]), 2
            )
        })

    benign_count = int(np.sum(predictions == 0))
    ddos_count = int(np.sum(predictions == 1))

    
    # CUVANJE BATCH ANALIZE U POSTGRESQL
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

                # 1. Cuvanje glavne batch analize
                cursor.execute(
                    """
                    INSERT INTO public.batch_analyses (
                        filename,
                        total_analyzed,
                        benign_count,
                        ddos_count
                    )
                    VALUES (%s, %s, %s, %s)
                    RETURNING id;
                    """,
                    (
                        file.filename,
                        len(results),
                        benign_count,
                        ddos_count
                    )
                )

                batch_id = cursor.fetchone()[0]

                # 2. Priprema pojedinacnih rezultata
                rows_to_insert = [
                    (
                        batch_id,
                        item["row"],
                        item["prediction"],
                        item["ddos_probability_percent"]
                    )
                    for item in results
                ]

                # 3. Cuvanje svih rezultata
                cursor.executemany(
                    """
                    INSERT INTO public.batch_prediction_results (
                        batch_id,
                        row_number,
                        prediction,
                        ddos_probability_percent
                    )
                    VALUES (%s, %s, %s, %s);
                    """,
                    rows_to_insert
                )

    except psycopg.Error:
        logger.exception(
            "Greska prilikom cuvanja batch analize"
        )

        raise HTTPException(
            status_code=503,
            detail="Batch analiza nije sacuvana u bazu."
        )


    return {
        "batch_id": batch_id,
        "filename": file.filename,
        "total_analyzed": len(results),
        "benign_count": benign_count,
        "ddos_count": ddos_count,
        "ddos_percentage": round(
            ddos_count / len(results) * 100, 2
        ),
        "results": results
    }

@router.get("/predictions/batches")
def get_batch_analyses():

    print("=== HISTORIJA BATCH ANALIZA ===")

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

                cursor.execute("""
                    SELECT
                        id,
                        filename,
                        total_analyzed,
                        benign_count,
                        ddos_count,
                        created_at
                    FROM public.batch_analyses
                    ORDER BY created_at DESC, id DESC;
                """)

                rows = cursor.fetchall()

    except psycopg.Error:
        logger.exception(
            "Greska prilikom ucitavanja batch historije"
        )

        raise HTTPException(
            status_code=503,
            detail="Nije moguce ucitati batch historiju."
        )

    batches = []

    for row in rows:
        batches.append({
            "batch_id": row[0],
            "filename": row[1],
            "total_analyzed": row[2],
            "benign_count": row[3],
            "ddos_count": row[4],
            "created_at": row[5].isoformat()
        })

    return {
        "count": len(batches),
        "batches": batches
    }


@router.get("/predictions/batches/stats")
def get_batch_statistics():

    print("=== UKUPNA STATISTIKA BATCH ANALIZA ===")

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

                cursor.execute("""
                    SELECT
                        COUNT(*) AS total_batches,

                        COALESCE(
                            SUM(total_analyzed), 0
                        ) AS total_records,

                        COALESCE(
                            SUM(benign_count), 0
                        ) AS benign_records,

                        COALESCE(
                            SUM(ddos_count), 0
                        ) AS ddos_records

                    FROM public.batch_analyses;
                """)

                result = cursor.fetchone()

    except psycopg.Error:
        logger.exception(
            "Greska prilikom ucitavanja batch statistike"
        )

        raise HTTPException(
            status_code=503,
            detail="Nije moguce ucitati batch statistiku."
        )

    total_batches = result[0]
    total_records = result[1]
    benign_records = result[2]
    ddos_records = result[3]

    ddos_percentage = (
        ddos_records / total_records * 100
        if total_records > 0 else 0
    )

    return {
        "total_batches": total_batches,
        "total_records": total_records,
        "benign_records": benign_records,
        "ddos_records": ddos_records,
        "ddos_percentage": round(ddos_percentage, 2)
    }


@router.get("/predictions/batches/timeline")
def get_batch_timeline(days: int | None = None):

    print("=== BATCH ANALIZE PO DANIMA ===")

    # Dozvoljavamo samo 7, 30 ili sve dane
    if days not in (None, 7, 30):
        raise HTTPException(
            status_code=422,
            detail="Dozvoljene vrijednosti su 7 ili 30."
        )

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

                cursor.execute("""
                    SELECT
                        DATE(created_at) AS day,
                        COUNT(*) AS total_batches,
                        SUM(total_analyzed) AS total_records,
                        SUM(benign_count) AS benign_count,
                        SUM(ddos_count) AS ddos_count

                    FROM public.batch_analyses

                    WHERE (
                        %s::integer IS NULL
                        OR created_at >=
                            NOW() - (%s::integer * INTERVAL '1 day')
                    )

                    GROUP BY DATE(created_at)
                    ORDER BY day ASC;
                """, (days, days))

                rows = cursor.fetchall()

    except psycopg.Error:
        logger.exception(
            "Greska prilikom ucitavanja batch timeline"
        )

        raise HTTPException(
            status_code=503,
            detail="Nije moguce ucitati batch timeline."
        )

    timeline = []

    for row in rows:
        timeline.append({
            "day": row[0].isoformat(),
            "total_batches": row[1],
            "total_records": row[2],
            "benign_count": row[3],
            "ddos_count": row[4]
        })

    return {
        "timeline": timeline
    }


@router.get("/predictions/batches/{batch_id}")
def get_batch_details(batch_id: int):

    print(f"=== DETALJI BATCH ANALIZE #{batch_id} ===")

    if batch_id < 1:
        raise HTTPException(
            status_code=422,
            detail="Batch ID mora biti veci od nule."
        )

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

                # Osnovni podaci o analizi
                cursor.execute("""
                    SELECT
                        id,
                        filename,
                        total_analyzed,
                        benign_count,
                        ddos_count,
                        created_at
                    FROM public.batch_analyses
                    WHERE id = %s;
                """, (batch_id,))

                batch = cursor.fetchone()

                if batch is None:
                    raise HTTPException(
                        status_code=404,
                        detail="Batch analiza nije pronadjena."
                    )

                # Pojedinacni rezultati analize
                cursor.execute("""
                    SELECT
                        row_number,
                        prediction,
                        ddos_probability_percent
                    FROM public.batch_prediction_results
                    WHERE batch_id = %s
                    ORDER BY row_number ASC;
                """, (batch_id,))

                rows = cursor.fetchall()

    except psycopg.Error:
        logger.exception(
            "Greska prilikom ucitavanja batch detalja"
        )

        raise HTTPException(
            status_code=503,
            detail="Nije moguce ucitati detalje batch analize."
        )

    results = []

    for row in rows:
        results.append({
            "row": row[0],
            "prediction": row[1],
            "ddos_probability_percent": round(row[2], 2)
        })

    return {
        "batch_id": batch[0],
        "filename": batch[1],
        "total_analyzed": batch[2],
        "benign_count": batch[3],
        "ddos_count": batch[4],
        "ddos_percentage": round(
            batch[4] / batch[2] * 100, 2
        ),
        "created_at": batch[5].isoformat(),
        "results": results
    }



