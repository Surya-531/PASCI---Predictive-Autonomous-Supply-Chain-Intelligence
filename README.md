# 🚚 PASCI – Predictive Autonomous Supply Chain Intelligence

**Advanced AI-powered supply chain prediction system with explainable AI and real-time route optimization.**

Combines machine learning, intelligent routing, and Google Gemini AI to predict shipment delays, generate human-readable explanations, and suggest optimized routes.

---

## ✨ What's New (AI Logistics Assistant)

- 🤖 **Gemini AI Integration:** Natural language explanations for every prediction
- 🗺️ **Route Visualization:** Interactive maps with Folium and Google Maps
- 📊 **Explainable AI:** Understand *why* delays happen and *what* to do
- ☁️ **Cloud Ready:** Docker & Google Cloud Run deployment included
- 🔍 **Production Grade:** Error handling, monitoring, CI/CD ready

---

## 📁 Project Structure

```
PASCI/
├── backend/
│   ├── app.py                  ← FastAPI REST API
│   └── gemini_helper.py        ← AI Logistics Assistant (NEW)
├── frontend/
│   └── app.py                  ← Streamlit dashboard with maps (UPDATED)
├── model/
│   ├── generate_data.py        ← Synthetic dataset generator
│   ├── train_model.py          ← Random Forest model
│   └── model.pkl               ← Trained model
├── optimization/
│   └── route_optimizer.py      ← Dijkstra-based routing
├── firebase/
│   └── firebase_config.py      ← Firestore integration
├── data/
│   └── data.csv                ← Generated training data
├── requirements.txt            ← All dependencies
├── Dockerfile                  ← Backend container (NEW)
├── Dockerfile.frontend         ← Frontend container (NEW)
├── validate.py                 ← Validation script (NEW)
├── deploy_to_cloud.py          ← Cloud deployment helper (NEW)
├── QUICKSTART.md               ← Quick setup guide (NEW)
├── CONFIG_GUIDE.md             ← Configuration guide (NEW)
├── DEPLOYMENT_GUIDE.md         ← Cloud deployment (NEW)
├── PRESENTATION_GUIDE.md       ← Pitch deck talking points (NEW)
└── README.md
```

---

## ⚙️ Installation

### Prerequisites
- Python 3.9+
- pip
- Git
- (Optional) Docker for containerization

### Setup

```bash
# 1. Clone or extract the project
cd PASCI

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Train the ML model
python model/generate_data.py
python model/train_model.py

# 5. Validate installation
python validate.py
```

---

## 🚀 Quick Start

### Step 1 – Generate data & train model
```bash
python setup.py
```
This creates `data/data.csv` and `model/model.pkl`.

### Step 2 – Start the API server
```bash
uvicorn backend.app:app --reload
```
API runs at **http://127.0.0.1:8000**  
Swagger docs → http://127.0.0.1:8000/docs

### Step 3 – Start the dashboard (new terminal)
```bash
streamlit run frontend/app.py
```
Dashboard opens at **http://localhost:8501**

---

## 🔥 Firebase Setup (optional)

The app works in **demo mode** without Firebase.  
To enable real persistence:

1. Go to https://console.firebase.google.com/
2. Create a project → **Project Settings → Service Accounts**
3. Click **Generate new private key** → download JSON
4. Replace `serviceAccountKey.json` with the downloaded file

---

## 🌐 API Reference

### `POST /predict`

**Request:**
```json
{
  "shipment_id": "S101",
  "distance":    300,
  "traffic":     2,
  "weather":     1
}
```

**Response:**
```json
{
  "shipment_id": "S101",
  "delay":       1,
  "risk":        0.82,
  "risk_pct":    "82.0%",
  "status":      "HIGH RISK",
  "route":       ["Chennai", "Salem", "Bangalore"],
  "all_routes":  [...],
  "alert":       true,
  "alert_msg":   "⚠️ ALERT: Shipment S101 has HIGH delay risk ...",
  "timestamp":   "2024-07-01T10:30:00+00:00",
  "firebase_doc":"abc123"
}
```

## 🚀 Running PASCI

### Option A: Backend + Frontend (Recommended)

**Terminal 1 – Backend API:**
```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 – Frontend Dashboard:**
```bash
streamlit run frontend/app.py
```

Visit: http://localhost:8501

### Option B: Frontend Only (Offline Mode)

```bash
streamlit run frontend/app.py
```

The app will use local ML inference (no API server needed).

### Option C: Validation

Before running, validate the setup:
```bash
python validate.py
```

---

## 🤖 AI Logistics Assistant Features

### What's Generated for Each Prediction

For every shipment prediction, the system generates:

1. **Delay Probability:** ML-predicted risk percentage
2. **Optimal Route:** Dijkstra-optimized path with traffic/weather penalties
3. **AI Explanation:** Natural language explanation from Gemini AI
   > *"Delay risk is HIGH due to storm conditions and heavy traffic. The suggested route via Salem reduces risk by 35% by avoiding the congested coastal highway."*
4. **Route Visualization:** Interactive map showing recommended and alternative routes
5. **Historical Data:** Saved to Firebase for trend analysis

### Example Predictions

```
Scenario 1: Good Conditions
- Distance: 150 km, Traffic: Low, Weather: Clear
- Risk: 5-10%
- Route: Direct (Chennai → Bangalore)
- Action: "Proceed as planned"

Scenario 2: Challenging
- Distance: 300 km, Traffic: High, Weather: Storm
- Risk: 82%
- Route: Detour (Chennai → Salem → Bangalore)
- Action: "High risk - consider reroute or delay shipment"
```

---

## 🗺️ Route Visualization

PASCI provides two map visualization options:

### 1. Interactive Folium Map (Default)
- No API key required
- Click-enabled interactive map
- Shows route with city markers
- Works offline

### 2. Google Maps (Optional)
- Professional routing visualization
- Real-time traffic layer support
- Requires Google Maps API key
- Better for production demos

Set `GOOGLE_MAPS_API_KEY` environment variable to enable.

---

## 🔑 API Configuration

### Gemini AI (Required for Explanations)

Get your API key at: https://aistudio.google.com/

```bash
# Windows PowerShell
$env:GEMINI_API_KEY="YOUR_KEY"

# Linux/macOS
export GEMINI_API_KEY="YOUR_KEY"
```

### Google Maps (Optional for Enhanced Visualization)

Get your API key at: https://console.cloud.google.com/

```bash
# Windows PowerShell
$env:GOOGLE_MAPS_API_KEY="YOUR_KEY"

# Linux/macOS
export GOOGLE_MAPS_API_KEY="YOUR_KEY"
```

### Firebase (Optional for Data Persistence)

1. Create Firebase project at https://console.firebase.google.com/
2. Download service account JSON
3. Replace `serviceAccountKey.json` in the project root

---

## 🌐 API Reference

### `POST /predict`

Predict delay risk and get optimized route with AI explanation.

**Request:**
```json
{
  "shipment_id": "S101",
  "distance":    300,
  "traffic":     2,
  "weather":     1
}
```

**Response:**
```json
{
  "shipment_id":   "S101",
  "delay":         1,
  "risk":          0.82,
  "risk_pct":      "82.0%",
  "status":        "HIGH RISK",
  "route":         ["Chennai", "Salem", "Bangalore"],
  "all_routes":    [...],
  "alert":         true,
  "alert_msg":     "⚠️ ALERT: Shipment S101 has HIGH delay risk ...",
  "timestamp":     "2024-07-01T10:30:00+00:00",
  "firebase_doc":  "abc123",
  "explanation":   "Delay risk is HIGH due to storm conditions and heavy traffic..."
}
```

### `GET /history?limit=10`

Get recent shipment predictions from Firebase.

### `GET /health`

Health check endpoint.

---

## 📊 Model Details

### Random Forest Classifier
- **Training Data:** 1,000 synthetic samples
- **Features:** Distance, Traffic Level, Weather
- **Target:** Delay (0 = no delay, 1 = delay)
- **Accuracy:** ~85% on test set

### Route Optimization
- **Algorithm:** Dijkstra's Shortest Path
- **Graph:** 6 cities, multiple routes
- **Dynamic Penalties:**
  - Traffic: 0-80 km units
  - Weather: 0-60 km units
- **Routes:** Top 3-5 alternatives provided

### AI Explanations
- **Model:** Google Generative AI (Gemini Pro)
- **Language:** Natural English
- **Context:** Considers risk level, weather, traffic, route
- **Fallback:** Templated explanation if API unavailable

---

## 🧪 Testing

### Unit Tests

```bash
# Validate all components
python validate.py

# Test route optimizer
python optimization/route_optimizer.py

# Test Gemini integration
python backend/gemini_helper.py
```

### API Testing

```bash
# Health check
curl http://localhost:8000/health

# Make prediction
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"distance": 300, "traffic": 2, "weather": 2}'
```

---

## ☁️ Deployment

### Google Cloud Run (Recommended)

Quick deployment:

```bash
python deploy_to_cloud.py \
  --gemini-key YOUR_GEMINI_API_KEY \
  --maps-key YOUR_MAPS_API_KEY
```

Or manual deployment:

```bash
# Deploy backend
gcloud run deploy pasci-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars GEMINI_API_KEY=YOUR_KEY

# Deploy frontend
gcloud run deploy pasci-frontend \
  --source . \
  --dockerfile Dockerfile.frontend \
  --platform managed \
  --region us-central1
```

### Docker

Build and run locally:

```bash
# Backend
docker build -t pasci-api .
docker run -p 8000:8000 pasci-api

# Frontend
docker build -f Dockerfile.frontend -t pasci-frontend .
docker run -p 8501:8501 pasci-frontend
```

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed instructions.

---

## 📖 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 5 minutes
- **[CONFIG_GUIDE.md](CONFIG_GUIDE.md)** - Configuration and API keys
- **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** - Cloud deployment
- **[PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md)** - Pitch deck talking points

---

## 🏆 Architecture Overview

```
┌─────────────────────┐
│  Streamlit Frontend │  → Interactive dashboard
│  (Route Viz, Maps)  │
└──────────┬──────────┘
           │
┌──────────▼──────────────┐
│   FastAPI Backend       │  → REST API
│   (health, predict)     │
└──────────┬──────────────┘
           │
    ┌──────┴──────────────────────┐
    │                             │
┌───▼─────────┐  ┌──────────────▼────┐
│   ML Model  │  │ Route Optimizer   │
│(Random      │  │ (Dijkstra + NX)   │
│ Forest)     │  │                   │
└─────────────┘  └──────────────────┘
    │                    │
    └──────────┬─────────┘
               │
        ┌──────▼──────────┐
        │  Gemini AI      │
        │  (Explanations) │
        └──────┬──────────┘
               │
        ┌──────▼──────────┐
        │  Firebase       │
        │  (Firestore)    │
        └─────────────────┘
```

---

## 🏆 Key Features

✅ **Explainable AI** - Gemini-powered natural language explanations  
✅ **ML Prediction** - Random Forest classifier on diverse scenarios  
✅ **Route Optimization** - Dijkstra algorithm with dynamic penalties  
✅ **Interactive Maps** - Folium + Google Maps visualization  
✅ **FastAPI Backend** - High-performance REST API  
✅ **Streamlit Frontend** - Professional dashboard UI  
✅ **Firebase Integration** - Persistent data storage  
✅ **Cloud Ready** - Docker + Google Cloud Run support  
✅ **Error Handling** - Graceful fallbacks and monitoring  
✅ **Offline Mode** - Works without external APIs  

---

## 🛠 Troubleshooting

| Problem | Solution |
|---------|----------|
| `model.pkl not found` | Run `python model/generate_data.py && python model/train_model.py` |
| Connection refused | Start API: `python -m uvicorn backend.app:app --reload` |
| Maps not showing | Install: `pip install --upgrade folium streamlit-folium` |
| Gemini error | Check API key and network connection |
| Port already in use | Use different port: `--port 8001` |

For more details, see [CONFIG_GUIDE.md](CONFIG_GUIDE.md).

---

## 📝 License

This project is provided as-is for educational and commercial use.

---

## 🤝 Contributing

To improve PASCI:
1. Test the current features
2. Report issues with details
3. Suggest enhancements

---

## 👥 Team

Built with ❤️ for supply chain innovation.

---

**Questions?** Check the [QUICKSTART.md](QUICKSTART.md) or [CONFIG_GUIDE.md](CONFIG_GUIDE.md).

**Ready to deploy?** See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md).

**Need presentation tips?** Check [PRESENTATION_GUIDE.md](PRESENTATION_GUIDE.md).

---

## 🚀 Next Steps

1. ✅ Run locally: `streamlit run frontend/app.py`
2. ✅ Get Gemini API key for full AI features
3. ✅ Deploy to Google Cloud Run
4. ✅ Integrate with real traffic data
5. ✅ Scale to production

**Your intelligent supply chain awaits!** 🚚
