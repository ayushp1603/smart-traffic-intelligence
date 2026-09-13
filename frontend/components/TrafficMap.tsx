"use client";

import { useEffect, useState } from "react";
import {
  MapContainer,
  TileLayer,
  Polyline,
  Popup,
} from "react-leaflet";

import "leaflet/dist/leaflet.css";

type Road = {
  id: number;
  name: string;
  road_type: string | null;
  reference_speed: number | null;
  geometry: string;
};

type Traffic = {
  observation_id: number;
  observed_at: string;
  current_speed: number | null;
  reference_speed: number | null;
  source: string | null;
  congestion_score: number | null;
  traffic_level: string | null;
};

type TrafficRoad = {
  road_id: number;
  road_name: string;
  road_type: string | null;
  reference_speed: number | null;
  traffic: Traffic | null;
};

type Coordinate = [number, number];

const defaultPosition: [number, number] = [
  28.605,
  77.305,
];

export default function TrafficMap() {
  const [roads, setRoads] = useState<Road[]>([]);
  const [traffic, setTraffic] = useState<TrafficRoad[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);

  // Fetch roads only once
  useEffect(() => {
    async function fetchRoads() {
      try {
        const response = await fetch(
          "http://localhost:8000/roads/"
        );

        if (!response.ok) {
          throw new Error("Failed to fetch roads");
        }

        const data: Road[] = await response.json();

        setRoads(data);
      } catch (err) {
        console.error(err);
        setError("Could not load roads from backend.");
      }
    }

    fetchRoads();
  }, []);

  // Fetch live traffic immediately and every 30 seconds
  useEffect(() => {
    async function fetchTraffic() {
      try {
        const response = await fetch(
          "http://localhost:8000/traffic/live"
        );

        if (!response.ok) {
          throw new Error("Failed to fetch traffic");
        }

        const data = await response.json();

        setTraffic(data.roads);
        setLastUpdated(new Date().toLocaleTimeString());

        setError(null);
      } catch (err) {
        console.error(err);
        setError("Could not load live traffic data.");
      } finally {
        setLoading(false);
      }
    }

    fetchTraffic();

    const interval = setInterval(() => {
      fetchTraffic();
    }, 30000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  function getCoordinates(geometry: string): Coordinate[] {
    const parsed = JSON.parse(geometry);

    return parsed.coordinates.map(
      ([longitude, latitude]: [number, number]) =>
        [latitude, longitude] as Coordinate
    );
  }

  function getTrafficForRoad(roadId: number) {
    return traffic.find(
      (item) => item.road_id === roadId
    );
  }

  function getTrafficColor(
    level: string | null | undefined
  ) {
    switch (level) {
      case "Low":
        return "green";

      case "Moderate":
        return "orange";

      case "High":
        return "red";

      case "Severe":
        return "darkred";

      default:
        return "gray";
    }
  }

  return (
    <div className="relative">
      <MapContainer
        center={defaultPosition}
        zoom={13}
        scrollWheelZoom={true}
        style={{
          height: "500px",
          width: "100%",
        }}
      >
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {roads.map((road) => {
          const trafficData =
            getTrafficForRoad(road.id);

          const trafficLevel =
            trafficData?.traffic?.traffic_level ?? null;

          const color =
            getTrafficColor(trafficLevel);

          return (
            <Polyline
              key={road.id}
              positions={getCoordinates(
                road.geometry
              )}
              pathOptions={{
                color,
                weight: 7,
              }}
            >
              <Popup>
                <div className="min-w-[220px]">
                  <h3 className="mb-2 text-lg font-bold">
                    {road.name}
                  </h3>

                  <p>
                    <strong>Type:</strong>{" "}
                    {road.road_type ?? "N/A"}
                  </p>

                  <p>
                    <strong>Reference Speed:</strong>{" "}
                    {road.reference_speed ?? "N/A"} km/h
                  </p>

                  {trafficData?.traffic ? (
                    <>
                      <hr className="my-2" />

                      <p>
                        <strong>
                          Current Speed:
                        </strong>{" "}
                        {trafficData.traffic
                          .current_speed ?? "N/A"}{" "}
                        km/h
                      </p>

                      <p>
                        <strong>
                          Congestion:
                        </strong>{" "}
                        {trafficData.traffic
                          .congestion_score !== null
                          ? `${(
                              trafficData.traffic
                                .congestion_score * 100
                            ).toFixed(0)}%`
                          : "N/A"}
                      </p>

                      <p>
                        <strong>
                          Traffic Level:
                        </strong>{" "}
                        {trafficLevel ?? "N/A"}
                      </p>

                      <p>
                        <strong>Source:</strong>{" "}
                        {trafficData.traffic
                          .source ?? "N/A"}
                      </p>
                    </>
                  ) : (
                    <p className="mt-2">
                      <strong>Traffic:</strong>{" "}
                      No data
                    </p>
                  )}
                </div>
              </Popup>
            </Polyline>
          );
        })}
      </MapContainer>

      {loading && (
        <div className="absolute left-4 top-4 z-[1000] rounded bg-white px-3 py-2 shadow">
          Loading traffic...
        </div>
      )}

      {error && (
        <div className="absolute left-4 top-4 z-[1000] rounded bg-red-100 px-3 py-2 text-red-700 shadow">
          {error}
        </div>
      )}

      {lastUpdated && (
        <div className="absolute right-4 top-4 z-[1000] rounded bg-white px-3 py-2 text-sm shadow">
          Updated: {lastUpdated}
        </div>
      )}

      <div className="absolute bottom-4 right-4 z-[1000] rounded-lg bg-white p-3 shadow">
        <p className="mb-2 font-bold">
          Traffic Level
        </p>

        <div className="space-y-1 text-sm">
          <div>🟢 Low</div>
          <div>🟠 Moderate</div>
          <div>🔴 High</div>
          <div>🟥 Severe</div>
        </div>
      </div>
    </div>
  );
}