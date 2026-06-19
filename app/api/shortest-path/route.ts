import { NextRequest, NextResponse } from "next/server";

interface RouteRequest {
  source: string;
  destination: string;
}

interface RouteResponse {
  path: string[];
  distance: number;
  time: string;
  alternate_routes?: string[][];
  coordinates?: [number, number][];
  geometry?: [number, number][];
}

export async function POST(request: NextRequest) {
  try {
    const body: RouteRequest = await request.json();
    const { source, destination } = body;

    // Validate input
    if (!source || !destination) {
      return NextResponse.json(
        { error: "Source and destination are required" },
        { status: 400 }
      );
    }

    // Call Python Flask API
    const flaskUrl = process.env.FLASK_API_URL || "http://localhost:5000";

    let response: Response;
    try {
      response = await fetch(`${flaskUrl}/predict`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          source: source,
          destination: destination,
        }),
      });
    } catch (fetchError) {
      // Only fall back to mock data when Flask is genuinely unreachable
      // (e.g. not started). Real validation errors are handled below.
      console.error("Flask API unreachable, using fallback mock data:", fetchError);
      return NextResponse.json(generateMockRoute(source, destination));
    }

    // Flask responded — propagate its result, or its error (e.g. unknown city)
    const data = await response.json();

    if (!response.ok) {
      return NextResponse.json(
        { error: data.error || "Failed to find route" },
        { status: response.status }
      );
    }

    return NextResponse.json(data as RouteResponse);
  } catch (error) {
    console.error("API Error:", error);
    return NextResponse.json(
      { error: "Internal server error" },
      { status: 500 }
    );
  }
}

// Mock data generator for testing without Flask
function generateMockRoute(source: string, destination: string): RouteResponse {
  // City coordinates (approximate)
  const cityCoords: { [key: string]: [number, number] } = {
    Delhi: [28.6139, 77.2090],
    Mumbai: [19.0760, 72.8777],
    Bangalore: [12.9716, 77.5946],
    Pune: [18.5204, 73.8567],
    Hyderabad: [17.3850, 78.4867],
    Chennai: [13.0827, 80.2707],
    Kolkata: [22.5726, 88.3639],
    Jaipur: [26.9124, 75.7873],
    Ahmedabad: [23.0225, 72.5714],
    Lucknow: [26.8467, 80.9462],
  };

  const sourceCoord = cityCoords[source] || [28.6139, 77.2090];
  const destCoord = cityCoords[destination] || [19.0760, 72.8777];

  // Calculate approximate distance (Haversine formula)
  const R = 6371; // Earth's radius in km
  const dLat = ((destCoord[0] - sourceCoord[0]) * Math.PI) / 180;
  const dLon = ((destCoord[1] - sourceCoord[1]) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos((sourceCoord[0] * Math.PI) / 180) *
      Math.cos((destCoord[0] * Math.PI) / 180) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  const distance = R * c;

  // Calculate time (assuming 60 km/h average speed)
  const hours = distance / 60;
  const timeString =
    hours < 1
      ? `${Math.round(hours * 60)} min`
      : `${Math.floor(hours)} hr ${Math.round((hours % 1) * 60)} min`;

  // Generate intermediate points
  const path = [source];
  
  // Add some intermediate cities based on direction
  const midLat = (sourceCoord[0] + destCoord[0]) / 2;
  const midLon = (sourceCoord[1] + destCoord[1]) / 2;
  
  let nearestCity = "";
  let minDist = Infinity;
  
  Object.entries(cityCoords).forEach(([city, coord]) => {
    if (city !== source && city !== destination) {
      const dist = Math.sqrt(
        Math.pow(coord[0] - midLat, 2) + Math.pow(coord[1] - midLon, 2)
      );
      if (dist < minDist) {
        minDist = dist;
        nearestCity = city;
      }
    }
  });

  if (nearestCity) {
    path.push(nearestCity);
  }
  
  path.push(destination);

  // Generate coordinates for the path
  const coordinates: [number, number][] = path.map(
    (city) => cityCoords[city] || sourceCoord
  );

  return {
    path,
    distance: parseFloat(distance.toFixed(2)),
    time: timeString,
    coordinates,
    alternate_routes: [],
  };
}
