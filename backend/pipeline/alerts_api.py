
import os
import logging
from datetime import datetime
from typing import Literal

import psycopg
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path
from pydantic import BaseModel, Field
from psycopg.rows import dict_row

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

router = APIRouter(prefix="/alerts", tags=["Security Alerts"])
logger = logging.getLogger(__name__)


def get_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        connect_timeout=5,
        row_factory=dict_row
    )


class AlertCreate(BaseModel):
    prediction: Literal["DDoS"]
    ddos_probability_percent: float = Field(ge=0, le=100)
    source: Literal["simulation"] = "simulation"


def serialize_alert(row):
    result = dict(row)
    for field in ("created_at", "resolved_at"):
        if isinstance(result.get(field), datetime):
            result[field] = result[field].isoformat()
    return result


@router.post("", status_code=201)
def create_alert(payload: AlertCreate):
    probability = payload.ddos_probability_percent

    # Jednostavna demonstracijska pravila za severity.
    # Nisu validiran sigurnosni risk score.
    if probability >= 95:
        severity = "Critical"
    elif probability >= 80:
        severity = "High"
    elif probability >= 50:
        severity = "Medium"
    else:
        severity = "Low"

    description = (
        "DDoS traffic classified during simulated network monitoring. "
        f"Model probability: {probability:.2f}%."
    )

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO public.security_alerts (
                        alert_type,
                        severity,
                        status,
                        description,
                        ddos_probability_percent,
                        source
                    )
                    VALUES ('DDoS', %s, 'Active', %s, %s, %s)
                    RETURNING *;
                    """,
                    (
                        severity,
                        description,
                        probability,
                        payload.source
                    )
                )
                alert = cursor.fetchone()

        return serialize_alert(alert)

    except psycopg.Error as exc:
        logger.exception("Failed to create security alert")
        raise HTTPException(
            status_code=503,
            detail="Security alert could not be saved."
        ) from exc


@router.get("/stats")
def get_alert_stats():
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT
                        COUNT(*) AS total,
                        COUNT(*) FILTER (
                            WHERE status = 'Active'
                        ) AS active,
                        COUNT(*) FILTER (
                            WHERE status = 'Resolved'
                        ) AS resolved,
                        COUNT(*) FILTER (
                            WHERE severity = 'Critical'
                            AND status = 'Active'
                        ) AS critical
                    FROM public.security_alerts;
                    """
                )
                return dict(cursor.fetchone())

    except psycopg.Error as exc:
        logger.exception("Failed to load alert statistics")
        raise HTTPException(
            status_code=503,
            detail="Alert statistics unavailable."
        ) from exc


@router.get("")
def get_alerts(
    status: Literal["All", "Active", "Resolved"] = "All",
    limit: int = Query(default=100, ge=1, le=500)
):
    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    SELECT *
                    FROM public.security_alerts
                    WHERE (%s = 'All' OR status = %s)
                    ORDER BY created_at DESC, id DESC
                    LIMIT %s;
                    """,
                    (status, status, limit)
                )
                rows = cursor.fetchall()

        alerts = [serialize_alert(row) for row in rows]
        return {"count": len(alerts), "alerts": alerts}

    except psycopg.Error as exc:
        logger.exception("Failed to load security alerts")
        raise HTTPException(
            status_code=503,
            detail="Security alerts unavailable."
        ) from exc


@router.patch("/{alert_id}/resolve")
def resolve_alert(alert_id: int):
    if alert_id < 1:
        raise HTTPException(status_code=400, detail="Invalid alert ID.")

    try:
        with get_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    UPDATE public.security_alerts
                    SET
                        status = 'Resolved',
                        resolved_at = NOW()
                    WHERE id = %s
                    AND status = 'Active'
                    RETURNING *;
                    """,
                    (alert_id,)
                )
                updated = cursor.fetchone()

                if updated is None:
                    cursor.execute(
                        "SELECT * FROM public.security_alerts WHERE id = %s;",
                        (alert_id,)
                    )
                    existing = cursor.fetchone()
                    if existing is None:
                        raise HTTPException(
                            status_code=404,
                            detail="Alert not found."
                        )
                    return serialize_alert(existing)

        return serialize_alert(updated)

    except psycopg.Error as exc:
        logger.exception("Failed to resolve security alert")
        raise HTTPException(
            status_code=503,
            detail="Security alert could not be resolved."
        ) from exc
