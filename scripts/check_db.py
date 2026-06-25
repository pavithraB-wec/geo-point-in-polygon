import os
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "geopoly"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

def find_zones(lon, lat):
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT id, name
                    FROM zones
                    WHERE ST_Contains(
                        geom,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    )
                """, (lon, lat))
                return cur.fetchall()
    finally:
        conn.close()

if __name__ == "__main__":
    rows = find_zones(80.2750, 13.0870)
    print({"matches": rows})