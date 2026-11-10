
import os
import json
import hashlib
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from pipeline.extract import extract_data, DATA_PATH

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def load_data():

    # EXTRACT: citamo podatke iz CSV-a
    records = extract_data()

    if not records:
        print("Nema podataka za unos.")
        return

    rows = []

    for position, record in enumerate(records, start=1):

        # Jedinstveni identifikator izvornog reda
        content = json.dumps(record, sort_keys=True)

        source = f"{DATA_PATH.name}:{position}:{content}"

        source_key = hashlib.sha256(
            source.encode("utf-8")
        ).hexdigest()

        rows.append((
            source_key,
            record["source_ip"],
            record["destination_ip"],
            record["protocol"],
            record["packets"],
            record["duration"]
        ))

    # LOAD: spremamo podatke u PostgreSQL
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    ) as connection:

        with connection.cursor() as cursor:

            cursor.executemany("""
                INSERT INTO raw_network_traffic (
                    source_key,
                    source_ip,
                    destination_ip,
                    protocol,
                    packets,
                    duration
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (source_key) DO NOTHING
            """, rows)

            print(
                "Novih zapisa:",
                cursor.rowcount
            )


if __name__ == "__main__":
    load_data()
