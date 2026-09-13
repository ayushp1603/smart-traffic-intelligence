import json
from pathlib import Path

import psycopg


DATABASE_URL = (
    "postgresql://"
    "traffic_admin:traffic_password@localhost:5432/smart_traffic"
)

OSM_FILE = Path("data/osm_roads.json")

IMPORTANT_TYPES = {
    "primary",
    "secondary",
    "tertiary",
}

REFERENCE_SPEEDS = {
    "primary": 60,
    "secondary": 50,
    "tertiary": 40,
}


def main():
    print("Loading OSM data...")

    with open(OSM_FILE, "r", encoding="utf-8") as file:
        data = json.load(file)

    elements = data.get("elements", [])

    selected_roads = []
    used_names = set()

    for element in elements:
        tags = element.get("tags", {})
        highway = tags.get("highway")
        name = tags.get("name")
        geometry = element.get("geometry", [])

        if highway not in IMPORTANT_TYPES:
            continue

        if not name:
            continue

        if name in used_names:
            continue

        if len(geometry) < 2:
            continue

        selected_roads.append(
            {
                "name": name,
                "road_type": highway,
                "reference_speed": REFERENCE_SPEEDS[highway],
                "geometry": geometry,
                "osm_id": element.get("id"),
            }
        )

        used_names.add(name)

        if len(selected_roads) >= 20:
            break

    print(f"Selected roads: {len(selected_roads)}")

    if not selected_roads:
        print("No suitable roads found.")
        return

    with psycopg.connect(DATABASE_URL) as connection:
        with connection.cursor() as cursor:

            inserted = 0

            for road in selected_roads:
                coordinates = road["geometry"]

                wkt_coordinates = ", ".join(
                    f"{point['lon']} {point['lat']}"
                    for point in coordinates
                )

                wkt = f"LINESTRING({wkt_coordinates})"

                cursor.execute(
                    """
                    INSERT INTO roads
                    (
                        name,
                        road_type,
                        reference_speed,
                        geometry
                    )
                    VALUES
                    (
                        %s,
                        %s,
                        %s,
                        ST_GeomFromText(%s, 4326)
                    )
                    """,
                    (
                        road["name"],
                        road["road_type"],
                        road["reference_speed"],
                        wkt,
                    ),
                )

                inserted += 1

                print(
                    f"Inserted: {road['name']} "
                    f"({road['road_type']})"
                )

        connection.commit()

    print()
    print(f"Successfully inserted {inserted} real OSM roads.")


if __name__ == "__main__":
    main()