"use client";

import { RouteData } from "@/app/page";
import { Clock, TrendingUp } from "lucide-react";

interface RouteDetailsProps {
  routeData: RouteData;
}

export default function RouteDetails({ routeData }: RouteDetailsProps) {
  return (
    <div className="bg-gradient-to-br from-white to-blue-50 rounded-2xl shadow-2xl p-6 border-2 border-primary-200">
      <h2 className="text-2xl font-black text-gray-900 mb-6 flex items-center gap-3">
        📊 Route Details
      </h2>

      {/* Distance */}
      <div className="mb-5 p-4 bg-white rounded-xl shadow-md border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <TrendingUp className="w-6 h-6 text-primary-600" />
            <div>
              <p className="text-sm font-bold text-gray-600">Distance</p>
              <p className="text-xs text-gray-500">🛣️ Real road distance via highways</p>
            </div>
          </div>
          <p className="text-2xl font-black text-gray-900">{routeData.distance.toFixed(2)} km</p>
        </div>
      </div>

      {/* Time */}
      <div className="mb-5 p-4 bg-white rounded-xl shadow-md border border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Clock className="w-6 h-6 text-green-600" />
            <div>
              <p className="text-sm font-bold text-gray-600">Est. Time</p>
              <p className="text-xs text-gray-500">🚗 Real-time driving estimate</p>
            </div>
          </div>
          <p className="text-2xl font-black text-gray-900">{routeData.time}</p>
        </div>
      </div>

      {/* Route Path */}
      <div className="mb-5 p-4 bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl border border-gray-300">
        <p className="text-sm font-bold text-gray-800 mb-3 flex items-center gap-2">
          🛣️ Route Path:
        </p>
        <div className="space-y-2">
          {routeData.path.map((city, index) => (
            <div key={index} className="flex items-center gap-3 text-base">
              {index === 0 && (
                <span className="flex items-center gap-2 font-bold text-green-700">
                  <span className="bg-green-500 rounded-full w-3 h-3"></span>
                  {city} <span className="text-xs font-medium text-gray-600">(Starting point)</span>
                </span>
              )}
              {index > 0 && index < routeData.path.length - 1 && (
                <span className="flex items-center gap-2 font-semibold text-blue-700">
                  <span className="bg-blue-500 rounded-full w-3 h-3"></span>
                  {city} <span className="text-xs font-medium text-gray-600">(Via)</span>
                </span>
              )}
              {index === routeData.path.length - 1 && index > 0 && (
                <span className="flex items-center gap-2 font-bold text-red-700">
                  <span className="bg-red-500 rounded-full w-3 h-3"></span>
                  {city} <span className="text-xs font-medium text-gray-600">(Destination)</span>
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Alternate Routes */}
      {routeData.alternate_routes && routeData.alternate_routes.length > 0 && (
        <div className="p-4 bg-gradient-to-br from-amber-50 to-orange-50 rounded-xl border border-amber-300">
          <p className="text-sm font-bold text-amber-900 mb-3">
            🔀 Alternate Routes Available:
          </p>
          <div className="space-y-2">
            {routeData.alternate_routes.slice(0, 2).map((route, idx) => (
              <div key={idx} className="text-sm font-medium text-amber-800">
                Route {idx + 1}: {route.join(" → ")}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
