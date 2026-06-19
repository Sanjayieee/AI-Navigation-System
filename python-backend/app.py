from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
import pickle
import os
from typing import List, Tuple, Dict, Any
import math
import json
import urllib.request
import urllib.error
import joblib
import numpy as np
import pandas as pd

# Public OSRM routing service — gives real road distance/duration/geometry
# (close to Google Maps). Override with the OSRM_URL env var if self-hosting.
OSRM_BASE = os.getenv("OSRM_URL", "https://router.project-osrm.org").rstrip("/")

# Feature columns the ML model was trained on (must match the order used in training)
ML_FEATURE_NAMES = ["distance_km", "road_type", "traffic_level", "time_of_day"]

app = Flask(__name__)
CORS(app)  # Enable CORS for Next.js frontend

# Global variables
road_network = None
city_locations = {}
ml_model = None  # ML model for travel time prediction

# Initialize city coordinates with REAL data (ALL major Indian cities)
CITY_COORDS = {
    # Tier-1 Metro Cities (Population > 10M)
    "Delhi": (28.6139, 77.2090),
    "Mumbai": (19.0760, 72.8777),
    "Bangalore": (12.9716, 77.5946),
    "Kolkata": (22.5726, 88.3639),
    "Chennai": (13.0827, 80.2707),
    "Hyderabad": (17.3850, 78.4867),
    
    # Tier-2 Major Cities (Population > 2M)
    "Pune": (18.5204, 73.8567),
    "Ahmedabad": (23.0225, 72.5714),
    "Jaipur": (26.9124, 75.7873),
    "Surat": (21.1702, 72.8311),
    "Lucknow": (26.8467, 80.9462),
    "Kanpur": (26.4499, 80.3319),
    "Nagpur": (21.1458, 79.0882),
    "Indore": (22.7196, 75.8577),
    "Bhopal": (23.2599, 77.4126),
    "Visakhapatnam": (17.6868, 83.2185),
    "Patna": (25.5941, 85.1376),
    "Vadodara": (22.3072, 73.1812),
    "Ludhiana": (30.9010, 75.8573),
    "Agra": (27.1767, 78.0081),
    "Nashik": (19.9975, 73.7898),
    "Rajkot": (22.3039, 70.8022),
    "Varanasi": (25.3176, 82.9739),
    "Meerut": (28.9845, 77.7064),
    "Faridabad": (28.4089, 77.3178),
    "Ghaziabad": (28.6692, 77.4538),
    
    # Tier-3 Important Cities (State Capitals & Major Centers)
    "Amritsar": (31.6340, 74.8723),
    "Allahabad": (25.4358, 81.8463),
    "Ranchi": (23.3441, 85.3096),
    "Howrah": (22.5958, 88.2636),
    "Coimbatore": (11.0168, 76.9558),
    "Jabalpur": (23.1815, 79.9864),
    "Gwalior": (26.2183, 78.1828),
    "Vijayawada": (16.5062, 80.6480),
    "Madurai": (9.9252, 78.1198),
    "Mysore": (12.2958, 76.6394),
    "Goa": (15.2993, 74.1240),
    "Chandigarh": (30.7333, 76.7794),
    "Thiruvananthapuram": (8.5241, 76.9366),
    "Kochi": (9.9312, 76.2673),
    "Guwahati": (26.1445, 91.7362),
    "Bhubaneswar": (20.2961, 85.8245),
    "Dehradun": (30.3165, 78.0322),
    "Raipur": (21.2514, 81.6296),
    "Jodhpur": (26.2389, 73.0243),
    "Kota": (25.2138, 75.8648),
    "Udaipur": (24.5854, 73.7125),
    
    # North India Cities
    "Shimla": (31.1048, 77.1734),
    "Jammu": (32.7266, 74.8570),
    "Srinagar": (34.0837, 74.7973),
    "Haridwar": (29.9457, 78.1642),
    "Rishikesh": (30.0869, 78.2676),
    "Muzaffarpur": (26.1225, 85.3906),
    "Aligarh": (27.8974, 78.0880),
    "Moradabad": (28.8389, 78.7378),
    "Saharanpur": (29.9680, 77.5460),
    "Gorakhpur": (26.7606, 83.3732),
    "Bareilly": (28.3640, 79.4150),
    "Jhansi": (25.4484, 78.5685),
    
    # South India Cities
    "Tiruchirappalli": (10.7905, 78.7047),
    "Salem": (11.6643, 78.1460),
    "Tirupati": (13.6288, 79.4192),
    "Vellore": (12.9165, 79.1325),
    "Warangal": (17.9689, 79.5941),
    "Guntur": (16.3067, 80.4365),
    "Nellore": (14.4426, 79.9865),
    "Kakinada": (16.9891, 82.2475),
    "Rajahmundry": (17.0005, 81.8040),
    "Tirunelveli": (8.7139, 77.7567),
    "Erode": (11.3410, 77.7172),
    "Thanjavur": (10.7870, 79.1378),
    "Mangalore": (12.9141, 74.8560),
    "Hubli": (15.3647, 75.1240),
    "Belgaum": (15.8497, 74.4977),
    "Gulbarga": (17.3297, 76.8343),
    
    # West India Cities
    "Aurangabad": (19.8762, 75.3433),
    "Kolhapur": (16.7050, 74.2433),
    "Solapur": (17.6599, 75.9064),
    "Jalgaon": (21.0077, 75.5626),
    "Bhavnagar": (21.7645, 72.1519),
    "Jamnagar": (22.4707, 70.0577),
    "Gandhinagar": (23.2156, 72.6369),
    "Anand": (22.5645, 72.9289),
    
    # East India Cities
    "Siliguri": (26.7271, 88.3953),
    "Durgapur": (23.5204, 87.3119),
    "Asansol": (23.6739, 86.9524),
    "Cuttack": (20.5124, 85.8829),
    "Rourkela": (22.2604, 84.8536),
    "Jamshedpur": (22.8046, 86.2029),
    "Dhanbad": (23.7957, 86.4304),
    "Bokaro": (23.6693, 86.1511),
    
    # Central India Cities
    "Gwalior": (26.2183, 78.1828),
    "Ujjain": (23.1765, 75.7885),
    "Sagar": (23.8388, 78.7378),
    "Ratlam": (23.3315, 75.0367),
    "Satna": (24.6005, 80.8322),
    "Bilaspur": (22.0797, 82.1409),
    "Korba": (22.3595, 82.7501),
    
    # Northeast India Cities
    "Shillong": (25.5788, 91.8933),
    "Imphal": (24.8170, 93.9368),
    "Agartala": (23.8315, 91.2868),
    "Aizawl": (23.7271, 92.7176),
    "Kohima": (25.6701, 94.1077),
    "Itanagar": (27.1022, 93.6919),
    "Dibrugarh": (27.4728, 94.9120),
    "Silchar": (24.8333, 92.7789),
    "Jodhpur": (26.2389, 73.0243),
    "Madurai": (9.9252, 78.1198),
    "Raipur": (21.2514, 81.6296),
    "Kota": (25.2138, 75.8648),
}


def load_graph():
    """Load or create road network graph"""
    global road_network
    
    cache_file = "road_network.pkl"
    
    if os.path.exists(cache_file):
        print("Loading cached road network...")
        with open(cache_file, "rb") as f:
            road_network = pickle.load(f)
    else:
        print("Creating new road network graph...")
        # Create a simple graph with city connections
        road_network = create_simplified_graph()
        
        # Save to cache
        with open(cache_file, "wb") as f:
            pickle.dump(road_network, f)
    
    print(f"Graph loaded with {road_network.number_of_nodes()} nodes and {road_network.number_of_edges()} edges")


def load_ml_model():
    """Load the trained ML model for travel time prediction"""
    global ml_model
    
    model_file = "../travel_time_model.pkl"
    
    if os.path.exists(model_file):
        print("Loading ML model for travel time prediction...")
        ml_model = joblib.load(model_file)
        print("ML model loaded successfully!")
    else:
        print("Warning: ML model not found. Using simple time calculation.")
        ml_model = None


def create_simplified_graph():
    """Create a road network with REAL distances for major Indian cities"""
    G = nx.Graph()
    
    # Add nodes (cities) with coordinates
    for city, coords in CITY_COORDS.items():
        G.add_node(city, pos=coords, lat=coords[0], lon=coords[1])
    
    # Add edges with REAL road distances (in km) from actual highway routes
    # Source: Google Maps actual driving distances + National Highway Network
    connections = [
        # === GOLDEN QUADRILATERAL (Main Arteries) ===
        ("Delhi", "Jaipur", 280),
        ("Jaipur", "Ahmedabad", 660),
        ("Ahmedabad", "Mumbai", 526),
        ("Mumbai", "Pune", 148),
        ("Pune", "Hyderabad", 559),
        ("Hyderabad", "Vijayawada", 275),
        ("Vijayawada", "Chennai", 432),
        ("Chennai", "Bangalore", 346),
        ("Bangalore", "Hyderabad", 569),
        ("Delhi", "Agra", 233),
        ("Agra", "Kanpur", 294),
        ("Kanpur", "Lucknow", 83),
        ("Lucknow", "Varanasi", 320),
        ("Varanasi", "Patna", 247),
        ("Patna", "Kolkata", 585),
        
        # === DELHI NCR & NORTH ===
        ("Delhi", "Ghaziabad", 19),
        ("Delhi", "Faridabad", 28),
        ("Delhi", "Meerut", 72),
        ("Delhi", "Gwalior", 319),
        ("Delhi", "Chandigarh", 243),
        ("Delhi", "Amritsar", 453),
        ("Delhi", "Ludhiana", 313),
        ("Delhi", "Dehradun", 248),
        ("Delhi", "Haridwar", 214),
        ("Chandigarh", "Amritsar", 229),
        ("Chandigarh", "Ludhiana", 98),
        ("Chandigarh", "Shimla", 113),
        ("Amritsar", "Ludhiana", 142),
        ("Amritsar", "Jammu", 210),
        ("Jammu", "Srinagar", 261),
        ("Haridwar", "Rishikesh", 20),
        ("Haridwar", "Dehradun", 52),
        ("Meerut", "Saharanpur", 68),
        ("Meerut", "Moradabad", 87),
        ("Ghaziabad", "Meerut", 60),
        ("Agra", "Gwalior", 119),
        ("Agra", "Jaipur", 239),
        ("Agra", "Jhansi", 231),
        ("Gwalior", "Jhansi", 103),
        
        # === UTTAR PRADESH ===
        ("Lucknow", "Kanpur", 83),
        ("Lucknow", "Allahabad", 200),
        ("Lucknow", "Gorakhpur", 273),
        ("Lucknow", "Bareilly", 252),
        ("Kanpur", "Allahabad", 194),
        ("Varanasi", "Allahabad", 125),
        ("Varanasi", "Gorakhpur", 231),
        ("Gorakhpur", "Patna", 277),
        ("Aligarh", "Agra", 90),
        ("Bareilly", "Moradabad", 84),
        
        # === RAJASTHAN ===
        ("Jaipur", "Jodhpur", 337),
        ("Jaipur", "Kota", 241),
        ("Jaipur", "Udaipur", 394),
        ("Jodhpur", "Udaipur", 254),
        ("Kota", "Indore", 294),
        ("Udaipur", "Ahmedabad", 254),
        
        # === GUJARAT ===
        ("Ahmedabad", "Surat", 263),
        ("Ahmedabad", "Vadodara", 110),
        ("Ahmedabad", "Rajkot", 217),
        ("Ahmedabad", "Gandhinagar", 23),
        ("Ahmedabad", "Indore", 423),
        ("Surat", "Vadodara", 151),
        ("Surat", "Mumbai", 281),
        ("Rajkot", "Jamnagar", 89),
        ("Rajkot", "Bhavnagar", 178),
        ("Vadodara", "Anand", 43),
        
        # === MAHARASHTRA ===
        ("Mumbai", "Pune", 148),
        ("Mumbai", "Nashik", 167),
        ("Mumbai", "Surat", 281),
        ("Mumbai", "Goa", 464),
        ("Pune", "Nashik", 209),
        ("Pune", "Solapur", 250),
        ("Pune", "Kolhapur", 237),
        ("Pune", "Aurangabad", 233),
        ("Pune", "Goa", 450),
        ("Nashik", "Aurangabad", 183),
        ("Nashik", "Indore", 515),
        ("Aurangabad", "Nagpur", 442),
        ("Nagpur", "Hyderabad", 502),
        ("Nagpur", "Indore", 330),
        ("Nagpur", "Bhopal", 353),
        ("Nagpur", "Raipur", 290),
        ("Nagpur", "Jabalpur", 270),
        ("Solapur", "Hyderabad", 309),
        ("Kolhapur", "Goa", 228),
        
        # === MADHYA PRADESH ===
        ("Indore", "Bhopal", 196),
        ("Indore", "Ujjain", 55),
        ("Bhopal", "Jabalpur", 332),
        ("Bhopal", "Gwalior", 423),
        ("Bhopal", "Nagpur", 353),
        ("Jabalpur", "Raipur", 341),
        ("Jabalpur", "Varanasi", 535),
        ("Ujjain", "Ratlam", 94),
        ("Satna", "Allahabad", 128),
        
        # === CHHATTISGARH ===
        ("Raipur", "Nagpur", 290),
        ("Raipur", "Bilaspur", 118),
        ("Raipur", "Bhubaneswar", 447),
        ("Bilaspur", "Korba", 91),
        
        # === TELANGANA & ANDHRA PRADESH ===
        ("Hyderabad", "Bangalore", 569),
        ("Hyderabad", "Chennai", 626),
        ("Hyderabad", "Pune", 559),
        ("Hyderabad", "Nagpur", 502),
        ("Hyderabad", "Vijayawada", 275),
        ("Hyderabad", "Visakhapatnam", 619),
        ("Hyderabad", "Warangal", 148),
        ("Vijayawada", "Visakhapatnam", 351),
        ("Vijayawada", "Guntur", 33),
        ("Vijayawada", "Tirupati", 274),
        ("Vijayawada", "Rajahmundry", 188),
        ("Visakhapatnam", "Rajahmundry", 193),
        ("Visakhapatnam", "Kakinada", 158),
        ("Guntur", "Nellore", 176),
        
        # === KARNATAKA ===
        ("Bangalore", "Chennai", 346),
        ("Bangalore", "Hyderabad", 569),
        ("Bangalore", "Mysore", 144),
        ("Bangalore", "Coimbatore", 362),
        ("Bangalore", "Mangalore", 352),
        ("Bangalore", "Hubli", 410),
        ("Mysore", "Coimbatore", 267),
        ("Mangalore", "Goa", 360),
        ("Hubli", "Belgaum", 102),
        ("Hubli", "Goa", 195),
        ("Belgaum", "Goa", 138),
        ("Gulbarga", "Hyderabad", 220),
        
        # === TAMIL NADU ===
        ("Chennai", "Bangalore", 346),
        ("Chennai", "Coimbatore", 507),
        ("Chennai", "Madurai", 462),
        ("Chennai", "Tiruchirappalli", 322),
        ("Chennai", "Vellore", 138),
        ("Chennai", "Tirupati", 138),
        ("Coimbatore", "Madurai", 215),
        ("Coimbatore", "Mysore", 267),
        ("Coimbatore", "Kochi", 193),
        ("Coimbatore", "Erode", 88),
        ("Madurai", "Tirunelveli", 151),
        ("Tiruchirappalli", "Madurai", 134),
        ("Tiruchirappalli", "Thanjavur", 59),
        ("Salem", "Coimbatore", 162),
        ("Salem", "Bangalore", 183),
        
        # === KERALA ===
        ("Kochi", "Thiruvananthapuram", 220),
        ("Kochi", "Coimbatore", 193),
        ("Thiruvananthapuram", "Madurai", 268),
        
        # === WEST BENGAL ===
        ("Kolkata", "Howrah", 5),
        ("Kolkata", "Patna", 585),
        ("Kolkata", "Ranchi", 424),
        ("Kolkata", "Bhubaneswar", 442),
        ("Kolkata", "Siliguri", 580),
        ("Kolkata", "Durgapur", 169),
        ("Kolkata", "Asansol", 213),
        ("Siliguri", "Guwahati", 407),
        ("Durgapur", "Asansol", 48),
        
        # === BIHAR & JHARKHAND ===
        ("Patna", "Kolkata", 585),
        ("Patna", "Varanasi", 247),
        ("Patna", "Ranchi", 333),
        ("Patna", "Muzaffarpur", 70),
        ("Ranchi", "Jamshedpur", 130),
        ("Ranchi", "Dhanbad", 164),
        ("Ranchi", "Bokaro", 107),
        ("Jamshedpur", "Kolkata", 266),
        ("Dhanbad", "Asansol", 114),
        
        # === ODISHA ===
        ("Bhubaneswar", "Kolkata", 442),
        ("Bhubaneswar", "Cuttack", 28),
        ("Bhubaneswar", "Visakhapatnam", 444),
        ("Bhubaneswar", "Rourkela", 344),
        ("Cuttack", "Rourkela", 318),
        
        # === NORTHEAST ===
        ("Guwahati", "Siliguri", 407),
        ("Guwahati", "Shillong", 103),
        ("Guwahati", "Dibrugarh", 436),
        ("Guwahati", "Imphal", 483),
        ("Guwahati", "Agartala", 599),
        ("Shillong", "Silchar", 314),
        ("Imphal", "Kohima", 146),
        ("Agartala", "Silchar", 184),
    ]
    
    for city1, city2, distance in connections:
        if city1 in G.nodes and city2 in G.nodes:
            G.add_edge(city1, city2, length=distance)
    
    return G


def haversine_distance(coord1: Tuple[float, float], coord2: Tuple[float, float]) -> float:
    """Calculate distance between two coordinates using Haversine formula"""
    R = 6371  # Earth's radius in kilometers
    
    lat1, lon1 = math.radians(coord1[0]), math.radians(coord1[1])
    lat2, lon2 = math.radians(coord2[0]), math.radians(coord2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_time(distance_km: float) -> str:
    """
    Calculate estimated travel time using ML model with REAL distance data
    - Uses trained RandomForest model (99.42% accuracy)
    - Input: Real road distance in kilometers
    - Output: Predicted travel time based on distance, road type, traffic, and time of day
    """
    global ml_model
    
    if ml_model is not None:
        # Use ML model for prediction with REAL features
        # Features: [distance_km, road_type, traffic_level, time_of_day]
        # Default: road_type=1 (highway), traffic_level=1.0 (normal), time_of_day=1 (afternoon)
        # Use a DataFrame with named columns so the values line up with the
        # feature names the model was fitted with (avoids sklearn warnings).
        features = pd.DataFrame([[distance_km, 1, 1.0, 1]], columns=ML_FEATURE_NAMES)
        hours = ml_model.predict(features)[0]
    else:
        # Fallback to simple calculation
        # Assuming average speed of 60 km/h
        hours = distance_km / 60
    
    if hours < 1:
        return f"{int(hours * 60)} min"
    else:
        h = int(hours)
        m = int((hours - h) * 60)
        return f"{h} hr {m} min"


def format_duration(seconds: float) -> str:
    """Format a duration in seconds as '<h> hr <m> min' (or '<m> min')."""
    total_minutes = int(round(seconds / 60.0))
    hours, minutes = divmod(total_minutes, 60)
    if hours <= 0:
        return f"{minutes} min"
    return f"{hours} hr {minutes} min"


def get_osrm_route(coordinates: List[List[float]]) -> Dict[str, Any]:
    """Query OSRM for real road distance, duration and geometry.

    Args:
        coordinates: ordered waypoints as [lat, lon] pairs.

    Returns:
        {"distance_km", "duration_s", "geometry": [[lat, lon], ...]} on success,
        or None if the routing service is unavailable / returns no route.
    """
    if not coordinates or len(coordinates) < 2:
        return None

    try:
        # OSRM expects "lon,lat" pairs separated by ";"
        waypoints = ";".join(f"{lon},{lat}" for lat, lon in coordinates)
        url = (
            f"{OSRM_BASE}/route/v1/driving/{waypoints}"
            "?overview=full&geometries=geojson"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "ai-navigation/1.0"})
        with urllib.request.urlopen(req, timeout=12) as resp:
            data = json.loads(resp.read().decode("utf-8"))

        if data.get("code") == "Ok" and data.get("routes"):
            route = data["routes"][0]
            # GeoJSON is [lon, lat]; convert to [lat, lon] for Leaflet
            geometry = [[lat, lon] for lon, lat in route["geometry"]["coordinates"]]
            return {
                "distance_km": route["distance"] / 1000.0,
                "duration_s": route["duration"],
                "geometry": geometry,
            }
    except (urllib.error.URLError, urllib.error.HTTPError, ValueError, KeyError, TimeoutError) as e:
        print(f"OSRM lookup failed ({e}); falling back to graph estimate")

    return None


def find_alternate_routes(
    G: nx.Graph,
    source: str,
    target: str,
    main_path: List[str] = None,
    k: int = 2,
) -> List[List[str]]:
    """Find up to k alternate routes that are genuinely different from the
    primary route shown to the user.

    Iterates candidate routes in increasing order of distance and keeps the
    ones that are not identical to the main path (or to an already-selected
    alternate). Excluding the exact main path is important because, when
    several routes tie on distance, the engine's "shortest" path can differ
    from the one displayed — otherwise an "alternate" could be the same route.
    """
    try:
        alternates: List[List[str]] = []

        for path in nx.shortest_simple_paths(G, source, target, weight='length'):
            # Skip the primary route the user is already seeing
            if main_path is not None and path == main_path:
                continue
            # Skip duplicates of an alternate we've already picked
            if path in alternates:
                continue

            alternates.append(path)
            if len(alternates) >= k:
                break

        return alternates
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []


@app.route('/predict', methods=['POST'])
def predict_route():
    """Main endpoint for route prediction"""
    try:
        data = request.get_json()
        source = data.get('source', '').strip().title()
        destination = data.get('destination', '').strip().title()
        
        if not source or not destination:
            return jsonify({"error": "Source and destination are required"}), 400
        
        # Check if cities exist in our graph
        if source not in road_network.nodes:
            return jsonify({"error": f"Source city '{source}' not found in network"}), 404
        
        if destination not in road_network.nodes:
            return jsonify({"error": f"Destination city '{destination}' not found in network"}), 404
        
        if source == destination:
            return jsonify({"error": "Source and destination cannot be the same"}), 400
        
        # Find shortest path using Dijkstra's algorithm
        try:
            path = nx.shortest_path(road_network, source, destination, weight='length')
            distance_km = nx.shortest_path_length(road_network, source, destination, weight='length')
            # Note: Our graph already stores distances in kilometers (not meters)
        except nx.NetworkXNoPath:
            return jsonify({"error": f"No route found between {source} and {destination}"}), 404
        
        # Get coordinates for the path
        coordinates = []
        for city in path:
            node_data = road_network.nodes[city]
            # Handle both formats: (lat, lon) tuple from 'pos' or separate 'lat'/'lon' keys
            if 'lat' in node_data and 'lon' in node_data:
                coordinates.append([node_data['lat'], node_data['lon']])
            elif 'pos' in node_data:
                lat, lon = node_data['pos']
                coordinates.append([lat, lon])
            elif city in CITY_COORDS:
                lat, lon = CITY_COORDS[city]
                coordinates.append([lat, lon])

        # Prefer real road data from OSRM (accurate distance/time/geometry,
        # close to Google Maps). Fall back to the graph estimate if OSRM is
        # unavailable so the app keeps working offline.
        osrm = get_osrm_route(coordinates)
        if osrm:
            distance_km = osrm["distance_km"]
            time_str = format_duration(osrm["duration_s"])
            geometry = osrm["geometry"]
        else:
            time_str = calculate_time(distance_km)
            geometry = coordinates

        # Find alternate routes (excluding the primary path shown above)
        alternate_routes = find_alternate_routes(road_network, source, destination, main_path=path, k=2)

        response = {
            "path": path,
            "distance": round(distance_km, 2),
            "time": time_str,
            "coordinates": coordinates,
            "geometry": geometry,
            "alternate_routes": alternate_routes
        }
        
        return jsonify(response)
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "graph_loaded": road_network is not None,
        "cities_available": list(CITY_COORDS.keys()) if road_network else []
    })


@app.route('/cities', methods=['GET'])
def get_cities():
    """Get list of available cities"""
    return jsonify({
        "cities": list(CITY_COORDS.keys())
    })


if __name__ == '__main__':
    print("Starting Flask API...")
    load_graph()
    load_ml_model()  # Load the trained ML model
    print("Flask API ready!")
    debug_enabled = os.getenv("FLASK_DEBUG", "").lower() in {"1", "true", "yes"}
    app.run(host='0.0.0.0', port=5000, debug=debug_enabled, use_reloader=debug_enabled)
