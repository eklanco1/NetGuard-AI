
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# Ucitavanje konfiguracije iz .env datoteke
load_dotenv(Path(__file__).resolve().parents[1] / ".env")


def transform_data():

    # Povezivanje s PostgreSQL bazom
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    ) as connection:

        with connection.cursor() as cursor:

            # SQL transformacija
            cursor.execute("""
                INSERT INTO processed_network_traffic (
                    raw_id,
                    source_ip,
                    destination_ip,
                    protocol,
                    packets,
                    duration,
                    packets_per_second
                )
                SELECT
                    id,
                    source_ip,
                    destination_ip,
                    protocol,
                    packets::INTEGER,
                    duration::NUMERIC,
                    ROUND(
                        packets::NUMERIC /
                        NULLIF(duration::NUMERIC, 0),
                        2
                    )
                FROM raw_network_traffic
                WHERE TRUE

                ON CONFLICT (raw_id) DO UPDATE SET
                    source_ip = EXCLUDED.source_ip,
                    destination_ip = EXCLUDED.destination_ip,
                    protocol = EXCLUDED.protocol,
                    packets = EXCLUDED.packets,
                    duration = EXCLUDED.duration,
                    packets_per_second = EXCLUDED.packets_per_second,
                    processed_at = CURRENT_TIMESTAMP;
            """)

            print(
                "Obradjeno ili azurirano zapisa:",
                cursor.rowcount
            )


if __name__ == "__main__":
    transform_data()
