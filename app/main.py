import os
from dotenv import load_dotenv
from fastapi import FastAPI, Query
import psycopg2

load_dotenv()

app = FastAPI(title="Geo Point in Polygon API")

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "polyogon-db"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres123"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

def get_conn():
    return psycopg2.connect(**DB_CONFIG)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/check-point")
def check_point(lon: float = Query(...), lat: float = Query(...)):
    conn = get_conn()
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
                rows = cur.fetchall()

        return {
            "point": {"lon": lon, "lat": lat},
            "inside_any_polygon": len(rows) > 0,
            "matches": [{"id": r[0], "name": r[1]} for r in rows]
        }
    finally:
        conn.close()