# 🚗 AI Navigation System

An intelligent route planning system built with **Next.js**, **Python**, **NetworkX**, and **OpenStreetMap** that finds optimal routes between cities using AI-powered pathfinding algorithms.

![AI Navigation System](https://img.shields.io/badge/Next.js-14-black) ![Python](https://img.shields.io/badge/Python-3.10+-blue) ![Flask](https://img.shields.io/badge/Flask-3.0-green) ![License](https://img.shields.io/badge/license-MIT-blue)

## ✨ Features

- 🗺️ **Interactive Map Visualization** using Leaflet.js
- 🎯 **Shortest Path Algorithm** (Dijkstra) powered by NetworkX
- 🤖 **AI-based Travel Time Prediction** using Random Forest
- 🛣️ **Alternate Route Suggestions**
- 📊 **Real-time Route Details** (distance, time, waypoints)
- 🎨 **Modern, Responsive UI** built with Tailwind CSS
- ⚡ **Fast API Communication** between Next.js and Flask

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (Next.js)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   MapView    │  │    Form      │  │   Details    │      │
│  │  (Leaflet)   │  │   (Input)    │  │   (Route)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/JSON
                          ▼
┌─────────────────────────────────────────────────────────────┐
│              Next.js API Route (/api/shortest-path)         │
│                    (Node.js Backend)                         │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/JSON
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask API (Python Backend)                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   NetworkX   │  │   OSMnx      │  │  ML Model    │      │
│  │  (Dijkstra)  │  │ (Map Data)   │  │ (Prediction) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Frontend** | Next.js 14 (App Router) | React framework with SSR |
| **UI Components** | React + TypeScript | Component library |
| **Styling** | Tailwind CSS | Utility-first CSS |
| **Map** | Leaflet.js | Interactive maps |
| **Icons** | Lucide React | Modern icon library |
| **Backend API** | Next.js API Routes | Server-side API endpoints |
| **Python API** | Flask + CORS | RESTful API server |
| **Pathfinding** | NetworkX | Graph algorithms |
| **Map Data** | OSMnx + OpenStreetMap | Real road network data |
| **ML Model** | scikit-learn (Random Forest) | Travel time prediction |
| **Data Processing** | pandas, numpy | Data manipulation |

## 📦 Installation

### Prerequisites

- **Node.js** 18+ and npm/yarn
- **Python** 3.10+
- **pip** (Python package manager)

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd ai_nav
```

### 2. Install Frontend Dependencies

```bash
npm install
# or
yarn install
```

### 3. Install Python Dependencies

```bash
cd python-backend
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

## 🚀 Running the Application

### Start Python Flask Server

```bash
cd python-backend
python app.py
```

The Flask API will start on `http://localhost:5000`

### Start Next.js Development Server

In a new terminal:

```bash
npm run dev
```

The Next.js app will start on `http://localhost:3000`

### Open in Browser

Navigate to `http://localhost:3000` and start planning routes!

## 📓 Jupyter Notebook

The project includes a Jupyter notebook demonstrating the ML model and pathfinding algorithms:

```bash
# Install Jupyter (if not installed)
pip install jupyter

# Run notebook
jupyter notebook navigation_model.ipynb
```

The notebook covers:
- Loading OpenStreetMap data with OSMnx
- Implementing Dijkstra's algorithm
- Training ML models for travel time prediction
- Visualizing routes

## 🔧 Configuration

### Environment Variables

Create a `.env.local` file in the root directory:

```env
FLASK_API_URL=http://localhost:5000
```


## 📡 API Endpoints

### Next.js API

#### POST `/api/shortest-path`

Request:
```json
{
  "source": "Delhi",
  "destination": "Mumbai"
}
```

Response:
```json
{
  "path": ["Delhi", "Jaipur", "Ahmedabad", "Mumbai"],
  "distance": 1420.5,
  "time": "23 hr 40 min",
  "coordinates": [[28.6139, 77.2090], ...],
  "alternate_routes": [["Delhi", "Surat", "Mumbai"]]
}
```

### Flask API

#### POST `/predict`

Same request/response format as above.

#### GET `/health`

Health check endpoint.

#### GET `/cities`

Returns list of available cities.

## 🎨 UI Components

### NavigationForm
- Source and destination input fields
- Quick select buttons for popular cities
- Validation and loading states

### MapView
- Interactive Leaflet map
- Route visualization with polylines
- Markers for source, destination, and waypoints
- Auto-zoom to fit route

### RouteDetails
- Distance and estimated time
- Step-by-step route path
- Alternate route suggestions

## 🧠 ML Model

The system uses a **Random Forest Regressor** trained on:
- **Distance** (km)
- **Road Type** (highway, national, state)
- **Traffic Level** (low, medium, high)
- **Time of Day** (morning, afternoon, night)

Model performance:
- Mean Absolute Error: ~0.15 hours
- R² Score: ~0.90

## 🗺️ How It Works

1. **User Input**: Enter source and destination cities
2. **API Call**: Frontend sends request to Next.js API route
3. **Flask Processing**: Next.js forwards request to Flask backend
4. **Graph Algorithm**: NetworkX computes shortest path using Dijkstra's algorithm
5. **ML Prediction**: Random Forest model predicts travel time
6. **Route Generation**: Creates coordinate array for map visualization
7. **Response**: Returns route data with path, distance, time, coordinates
8. **Visualization**: Frontend displays route on interactive map

## 📂 Project Structure

```
ai_nav/
├── app/
│   ├── api/
│   │   └── shortest-path/
│   │       └── route.ts          # Next.js API endpoint
│   ├── layout.tsx                 # Root layout
│   ├── page.tsx                   # Main page
│   └── globals.css                # Global styles
├── components/
│   ├── NavigationForm.tsx         # Input form component
│   ├── MapView.tsx                # Map visualization
│   └── RouteDetails.tsx           # Route information display
├── python-backend/
│   ├── app.py                     # Flask API server
│   ├── requirements.txt           # Python dependencies
│   └── road_network.pkl           # Cached graph data
├── navigation_model.ipynb         # Jupyter notebook
├── package.json                   # Node dependencies
├── tsconfig.json                  # TypeScript config
├── tailwind.config.ts             # Tailwind config
└── README.md                      # This file
```

## 🧪 Testing

### Test Flask API

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{"source": "Delhi", "destination": "Mumbai"}'
```

### Test Next.js API

```bash
curl -X POST http://localhost:3000/api/shortest-path \
  -H "Content-Type: application/json" \
  -d '{"source": "Delhi", "destination": "Mumbai"}'
```

## 🚀 Deployment

### Deploy Next.js to Vercel

```bash
npm install -g vercel
vercel
```

### Deploy Flask to Heroku/Railway

1. Add `Procfile`:
```
web: cd python-backend && gunicorn app:app
```

2. Add `gunicorn` to requirements.txt

3. Deploy:
```bash
git push heroku main
```

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a pull request

## 📄 License

MIT License - feel free to use this project for learning or commercial purposes.

## 👨‍💻 Author

Built with ❤️ for learning and demonstration purposes.

## 🙏 Acknowledgments

- **OSMnx** for OpenStreetMap integration
- **NetworkX** for graph algorithms
- **Leaflet** for beautiful maps
- **Next.js** team for the amazing framework
- **OpenStreetMap** contributors

## 📞 Support

For issues or questions, please open a GitHub issue.

---

**Happy Route Planning! 🗺️✨**
