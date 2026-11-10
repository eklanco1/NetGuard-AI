
import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv


# Ucitavanje konfiguracije baze
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


def create_prediction_table():

    print("=== KREIRANJE TABELE ZA AI PREDIKCIJE ===")

    # Povezivanje s PostgreSQL bazom
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    ) as connection:

        with connection.cursor() as cursor:
            
            # Provjera na koju bazu smo povezani
            cursor.execute("""
                SELECT
                    current_database(),
                    current_schema(),
                    inet_server_addr(),
                    inet_server_port();
            """)

            print("\n=== PODACI O KONEKCIJI ===")
            print("Baza, shema, server i port:")
            print(cursor.fetchone())


            cursor.execute("""
                CREATE TABLE IF NOT EXISTS ai_prediction_history (
            
                    id BIGSERIAL PRIMARY KEY,
                    prediction VARCHAR(10) NOT NULL
                        CHECK (prediction IN ('BENIGN', 'DDoS')),
                    ddos_probability_percent DOUBLE PRECISION NOT NULL
                        CHECK (
                            ddos_probability_percent >= 0
                            AND ddos_probability_percent <= 100
                        ),
                    created_at TIMESTAMPTZ NOT NULL
                        DEFAULT CURRENT_TIMESTAMP
                );
            """)

            print("Tabela ai_prediction_history je spremna!")

    cursor.execute("""
                ALTER TABLE public.ai_prediction_history
                ADD COLUMN IF NOT EXISTS features JSONB;
            """)

    print("\n=== KREIRANJE ZAVRSENO ===")


if __name__ == "__main__":
    create_prediction_table()
