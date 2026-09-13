"use client";

import TrafficMap from "@/components/TrafficMap";

export default function Home() {
  return (
    <main className="min-h-screen bg-gray-100 p-6">
      <div className="mx-auto max-w-7xl">
        <h1 className="mb-2 text-3xl font-bold text-gray-900">
          Smart Traffic Intelligence
        </h1>

        <p className="mb-6 text-gray-600">
          Traffic monitoring and urban mobility platform
        </p>

        <div className="overflow-hidden rounded-xl bg-white shadow">
          <TrafficMap />
        </div>
      </div>
    </main>
  );
}