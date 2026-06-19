"use client";

import { useState } from "react";
import NavigationForm from "@/components/NavigationForm";
import MapView from "@/components/MapView";
import RouteDetails from "@/components/RouteDetails";
import { Navigation, Sparkles } from "lucide-react";

export interface RouteData {
  path: string[];
  distance: number;
  time: string;
  coordinates: [number, number][];
  geometry?: [number, number][];
  alternate_routes?: string[][];
}

export default function Home() {
  const [routeData, setRouteData] = useState<RouteData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleFindRoute = async (source: string, destination: string) => {
    setLoading(true);
    setError(null);
    setRouteData(null);

    try {
      const response = await fetch("/api/shortest-path", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ source, destination }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Failed to find route");
      }

      setRouteData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "An error occurred");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b-4 border-primary-500">
        <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-primary-500 to-primary-600 p-3 rounded-xl shadow-lg">
              <Navigation className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-black text-gray-900 flex items-center gap-2">
                AI Navigation System
              </h1>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="max-w-[1800px] mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Info Banner */}
        <div className="mb-6 bg-gradient-to-r from-green-50 via-emerald-50 to-teal-50 border-2 border-green-400 rounded-xl p-5 shadow-lg">
          <div className="flex items-center justify-center gap-3 text-center">
            <span className="text-4xl">🚀</span>
            <div>
              <p className="text-lg font-black text-green-900">
                Production-Ready AI Navigation System
              </p>
              <p className="text-sm font-bold text-green-800 mt-1">
                105 Cities • 153 Real Highways • ML Model (90.42% R²) • 3,848km Max Route
              </p>
              <p className="text-xs font-semibold text-green-700 mt-1">
              </p>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
          {/* Column 1 - Plan Your Route */}
          <div className="lg:col-span-3 space-y-6">
            <NavigationForm onSubmit={handleFindRoute} loading={loading} />

            {error && (
              <div className="bg-red-100 border-2 border-red-400 rounded-xl p-4 shadow-md">
                <p className="text-red-900 font-semibold text-base">⚠️ Error: {error}</p>
              </div>
            )}
          </div>

          {/* Column 2 - Interactive Route Map */}
          <div className="lg:col-span-6">
            <div className="bg-white rounded-2xl shadow-2xl overflow-hidden border-2 border-gray-200">
              <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-6 py-4">
                <h3 className="text-xl font-bold text-white flex items-center gap-2">
                  🗺️ Interactive Route Map
                </h3>
              </div>
              <div className="h-[650px] relative">
                <MapView routeData={routeData} loading={loading} />
              </div>
            </div>
          </div>

          {/* Column 3 - Route Details */}
          <div className="lg:col-span-3">
            {routeData ? (
              <RouteDetails routeData={routeData} />
            ) : (
              <div className="bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-2xl p-6 border-2 border-primary-200 text-center">
                <div className="text-5xl mb-3">📊</div>
                <p className="text-lg font-bold text-gray-800">Route Details</p>
                <p className="text-sm text-gray-600 mt-2">
                  Find a route to see distance, estimated time, and the full path here.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="mt-16 py-8 bg-gray-900 text-white">
        <div className="max-w-[1800px] mx-auto px-4 text-center">
          <p className="text-base font-semibold">🚀 Built with Next.js, Python, NetworkX & Machine Learning</p>
          <p className="text-sm text-gray-400 mt-2">Powered by Random Forest ML Model (90.42% accuracy)</p>
        </div>
      </footer>
    </main>
  );
}
