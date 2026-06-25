# Geo Point-in-Polygon Repo

Complete example for:
- storing polygons in PostgreSQL/PostGIS,
- checking whether a point is inside a polygon with Python/Shapely,
- exposing the check through FastAPI.

## What this repo contains
- SQL schema for PostGIS.
- Python scripts for local and DB checks.
- FastAPI service.
- Docker setup for PostgreSQL + PostGIS.

## Folder structure
```text
.
├── app/
│   ├── __init__.py
│   └── main.py
|   └── flask_app.py
├── sql/
│   └── schema.sql
├── scripts/
│   ├── check_local.py
│   └── check_db.py
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

## Prerequisites
- Docker and Docker Compose
- Python 3.10+
- PostgreSQL with PostGIS available in your environment, or use the Docker service below

## Quick start with Docker
1. Copy `.env.example` to `.env`.
2. Run `docker compose up -d`.
3. Create the schema using the SQL in `sql/schema.sql`.
4. Insert sample data.
5. Run the FastAPI app locally.

## 1) Start the database
```bash
docker compose up -d
```

## 2) Create schema
Open psql against the database, then run:
```bash
psql -h localhost -p 5432 -U postgres -d geopoly -f sql/schema.sql
```

## 3) Insert sample polygon
```sql
INSERT INTO zones (name, geom)
VALUES (
    'zone_a',
    ST_SetSRID(
        ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[80.2707,13.0827],[80.2807,13.0827],[80.2807,13.0927],[80.2707,13.0927],[80.2707,13.0827]]]}'),
        4326
    )
);
```

## 4) Run local Python check
```bash
python scripts/check_local.py
```

## 5) Run DB check script
```bash
python scripts/check_db.py
```

## 6) Run FastAPI
```bash
uvicorn app.main:app --reload
```

## 7) Run Flask
```bash
python app/flask_app.py
```

Test Flask:
```bash
curl "http://127.0.0.1:5000/check-point?lon=80.2750&lat=13.0870"
```

## Notes
- Use `(lon, lat)` order everywhere.
- `ST_Contains` checks whether the point is strictly inside the polygon.
- If you want boundary points included, use `ST_Intersects` instead.

## ✅ What repo already provides

project already contains the right pieces:

- `sql/schema.sql` — table creation plus PostGIS setup
- `scripts/check_db.py` — DB query using `ST_Contains`
- `app/main.py` — FastAPI endpoint for point-in-polygon checks
- `requirements.txt` — Python dependencies
- `.env.example` — environment variables for DB connection

So the main remaining step is: **run a local PostgreSQL server with PostGIS enabled** and connect the app to it.

---

## 🔧 Local PostgreSQL + PostGIS setup with pgAdmin

Since `psql` is not available, use pgAdmin or install PostgreSQL with CLI tools.

### 1) Verify PostgreSQL server
If pgAdmin works, open it and check whether a PostgreSQL server is registered and running.

### 2) Create the database
In pgAdmin:
- Create a database named: `geopoly`

### 3) Enable PostGIS
Run this in pgAdmin Query Tool for the `geopoly` database:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

### 4) Create the `zones` table
Run the SQL in `sql/schema.sql`, or copy this:
```sql
CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS zones (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    geom geometry(Polygon, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS zones_geom_idx
ON zones
USING GIST (geom);
```

---

## 🧩 Insert a polygon

Use GeoJSON or WKT. Example GeoJSON insertion:
```sql
INSERT INTO zones (name, geom)
VALUES (
  'zone_a',
  ST_SetSRID(
    ST_GeomFromGeoJSON('{"type":"Polygon","coordinates":[[[80.2707,13.0827],[80.2807,13.0827],[80.2807,13.0927],[80.2707,13.0927],[80.2707,13.0827]]]}'),
    4326
  )
);
```

---

## ▶️ Query whether a point is inside

This is the exact pattern your code should use:

```sql
SELECT id, name
FROM zones
WHERE ST_Contains(
    geom,
    ST_SetSRID(ST_MakePoint(80.2750, 13.0870), 4326)
);
```

If you want boundary-touching points to count too, use:

```sql
SELECT id, name
FROM zones
WHERE ST_Intersects(
    geom,
    ST_SetSRID(ST_MakePoint(80.2750, 13.0870), 4326)
);
```

---

## ✅ Expected output

For the point-in-polygon system, the expected output is:

- whether the point is inside any stored polygon
- the matching polygon record(s), usually `id` and `name`

### If using the FastAPI endpoint
A successful response should look like:

```json
{
  "point": { "lon": 80.2750, "lat": 13.0870 },
  "inside_any_polygon": true,
  "matches": [
    { "id": 1, "name": "zone_a" }
  ]
}
```

If no polygon matches:

```json
{
  "point": { "lon": 80.2750, "lat": 13.0870 },
  "inside_any_polygon": false,
  "matches": []
}
```

### If using the direct DB query
A query like:

```sql
SELECT id, name
FROM zones
WHERE ST_Contains(
    geom,
    ST_SetSRID(ST_MakePoint(80.2750, 13.0870), 4326)
);
```

should return one or more rows with `id` and `name` for matching polygons.

---

## 🧪 Sample input and output

### Input
- Point: `lon=80.2750`, `lat=13.0870`
- Stored polygon: a rectangle covering the area between
  `(80.2707, 13.0827)` and `(80.2807, 13.0927)`.

### Output for FastAPI
```json
{
  "point": { "lon": 80.2750, "lat": 13.0870 },
  "inside_any_polygon": true,
  "matches": [
    { "id": 1, "name": "zone_a" }
  ]
}
```

### Output for direct DB query
Rows returned:

| id | name   |
|----|--------|
| 1  | zone_a |

---

## 📝 Configure your `.env`

Create `.env` in repo root with your actual local values:
```env
POSTGRES_DB=geopoly
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
```

code already reads these values in `app/main.py` and `scripts/check_db.py`.

---

## 🚀 Run the API

Install dependencies, then start FastAPI:
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Test:
```bash
curl "http://127.0.0.1:8000/check-point?lon=80.2750&lat=13.0870"
```

---

## 📌 Summary

This is a correct implementation path for the assignment:
- store polygons in PostGIS,
- use `ST_Contains` for containment,
- optionally use `ST_Intersects` for boundary-inclusion,
- return matching polygon `id`/`name`.

