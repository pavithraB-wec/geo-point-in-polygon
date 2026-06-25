from shapely.geometry import Point, Polygon

lon, lat = 80.2750, 13.0870
point = Point(lon, lat)

polygon = Polygon([
    (80.2707, 13.0827),
    (80.2807, 13.0827),
    (80.2807, 13.0927),
    (80.2707, 13.0927),
    (80.2707, 13.0827),
])

print({"point": [lon, lat], "inside": polygon.contains(point)})