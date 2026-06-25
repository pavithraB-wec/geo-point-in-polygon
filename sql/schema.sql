CREATE EXTENSION IF NOT EXISTS postgis;

CREATE TABLE IF NOT EXISTS zones (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    geom geometry(Polygon, 4326) NOT NULL
);

CREATE INDEX IF NOT EXISTS zones_geom_idx
ON zones
USING GIST (geom);