import os
from dotenv import load_dotenv
from flask import Flask, jsonify, request
import psycopg2

load_dotenv()

app = Flask(__name__)

DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "geopoly"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}


def get_conn():
    return psycopg2.connect(**DB_CONFIG)


@app.route("/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/check-point")
def check_point():
    lon = request.args.get("lon")
    lat = request.args.get("lat")
    if lon is None or lat is None:
        return jsonify({"detail": "lon and lat query parameters are required"}), 400

    try:
        lon = float(lon)
        lat = float(lat)
    except ValueError:
        return jsonify({"detail": "lon and lat must be numbers"}), 400

    try:
        conn = get_conn()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT id, name
                    FROM zones
                    WHERE ST_Contains(
                        geom,
                        ST_SetSRID(ST_MakePoint(%s, %s), 4326)
                    )
                    """,
                    (lon, lat),
                )
                rows = cur.fetchall()
    except psycopg2.Error as exc:
        return jsonify({"detail": "database error", "error": str(exc)}), 500
    finally:
        if "conn" in locals() and conn is not None:
            conn.close()

    return jsonify({
        "point": {"lon": lon, "lat": lat},
        "inside_any_polygon": len(rows) > 0,
        "matches": [{"id": r[0], "name": r[1]} for r in rows],
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
