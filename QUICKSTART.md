# PASCI Quick Start Guide

Get PASCI running locally in 5 minutes! 🚀

## Prerequisites

- Python 3.9+
- pip
- Git

## Installation

### 1. Clone/Set Up the Project

```bash
cd PASCI
```

### 2. Create Virtual Environment (Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Train the ML Model

This creates the machine learning model that predicts delays:

```bash
python model/generate_data.py
python model/train_model.py
```

Expected output: `model/model.pkl` (~2MB file created)

---

## Running the System

### Option A: Run Backend + Frontend Locally

**Terminal 1 – Start Backend API:**

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
Press CTRL+C to quit
```

**Terminal 2 – Start Frontend (new terminal):**

```bash
streamlit run frontend/app.py
```

Expected output:
```
You can now view your Streamlit app in your browser.
Local URL: http://localhost:8501
```

**Visit the app:** http://localhost:8501

---

### Option B: Run Frontend in Offline Mode

If you don't want to run the backend API:

```bash
streamlit run frontend/app.py
```

The frontend will automatically fall back to local ML inference. ✅

---

## Using the App

### 1. Configure Shipment Details (Sidebar)

- **Distance:** 50–500 km (drag slider)
- **Traffic Level:** Low / Medium / High
- **Weather Condition:** Clear / Rain / Storm

### 2. Click "Predict" Button

The app will:
- Predict delay risk
- Suggest optimal route
- Generate AI explanation via Gemini
- Show route visualization

### 3. View Results

You'll see:
- ✅ Delay probability
- ✅ Best route recommendation
- ✅ AI Logistics Assistant explanation
- ✅ Interactive map (Folium)
- ✅ Alternative routes ranked by cost

---

## Example Predictions

### Low Risk Scenario
- Distance: 150 km
- Traffic: Low
- Weather: Clear
- **Expected:** Risk 10-20%
- **Route:** Direct path (Chennai → Bangalore)

### High Risk Scenario
- Distance: 300 km
- Traffic: High
- Weather: Storm
- **Expected:** Risk 70-90%
- **Route:** Detour via Salem/Vellore to avoid worst traffic

### Medium Risk Scenario
- Distance: 250 km
- Traffic: Medium
- Weather: Rain
- **Expected:** Risk 40-60%
- **Route:** Balanced between direct and safe

---

## API Usage (Backend Only)

### Health Check

```bash
curl http://localhost:8000/health
```

Response:
```json
{"status": "ok", "service": "PASCI API"}
```

### Make Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 300,
    "traffic": 2,
    "weather": 2
  }'
```

Response includes:
- `delay`: 0 or 1 (predicted delay)
- `risk`: 0.0-1.0 (probability)
- `route`: Suggested path
- `explanation`: AI-generated explanation
- `alert`: True if high risk

### Get History

```bash
curl http://localhost:8000/history?limit=10
```

---

## Configuration

### Environment Variables

Set these before running for full features:

**Windows PowerShell:**
```powershell
$env:GEMINI_API_KEY="YOUR_API_KEY"
$env:GOOGLE_MAPS_API_KEY="YOUR_MAPS_API_KEY"
```

**macOS/Linux:**
```bash
export GEMINI_API_KEY="YOUR_API_KEY"
export GOOGLE_MAPS_API_KEY="YOUR_MAPS_API_KEY"
```

### Get API Keys

1. **Gemini API Key:**
   - Visit: https://aistudio.google.com/
   - Click "Create API Key"
   - Copy key

2. **Google Maps API Key (Optional):**
   - Visit: https://console.cloud.google.com/
   - Enable Maps API
   - Create API key
   - If not set, Folium map is used (no key needed)

---

## Testing

### Test Gemini Integration

```bash
python backend/gemini_helper.py
```

Expected output: Generated AI explanation for sample shipment

### Test Route Optimizer

```bash
python optimization/route_optimizer.py
```

Expected output: Sample routes for different traffic/weather scenarios

### Test Model

```bash
python model/train_model.py --test
```

Expected output: Model accuracy metrics

---

## Troubleshooting

### Issue: Port 8000 already in use

**Solution:**
```bash
# Use different port
python -m uvicorn backend.app:app --port 8001
```

### Issue: Port 8501 already in use

**Solution:**
```bash
# Kill the process using port 8501
# Windows: netstat -ano | findstr :8501
# macOS/Linux: lsof -i :8501
```

### Issue: Model not found

**Solution:**
```bash
# Retrain model
python model/generate_data.py
python model/train_model.py
```

### Issue: Gemini API returns error

**Solution:**
- Check API key is set correctly
- Verify API key hasn't been revoked
- Check internet connection
- Wait a moment (rate limiting)

### Issue: Maps not displaying

**Solution:**
- Ensure folium and streamlit-folium are installed
- Check city names are valid
- Try: `pip install --upgrade folium streamlit-folium`

### Issue: Firebase connection fails

**Solution:**
- Ensure `serviceAccountKey.json` exists
- Verify Firebase credentials
- System works fine without Firebase (offline mode)

---

## Project Structure

```
PASCI/
├── frontend/              # Streamlit UI
│   └── app.py
├── backend/               # FastAPI API
│   ├── app.py
│   └── gemini_helper.py   # AI explanation
├── model/                 # ML model
│   ├── generate_data.py
│   └── train_model.py
├── optimization/          # Route optimizer
│   └── route_optimizer.py
├── firebase/              # Firebase integration
│   └── firebase_config.py
├── data/                  # Sample data
│   └── data.csv
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker for backend
└── CONFIG_GUIDE.md        # Detailed config
```

---

## Common Commands

```bash
# List running processes
netstat -ano

# Kill process on port 8000
# Windows: taskkill /PID <PID> /F
# macOS/Linux: kill -9 <PID>

# Check Python version
python --version

# List installed packages
pip list

# Upgrade a package
pip install --upgrade package-name

# View requirements
cat requirements.txt
```

---

## Next Steps

1. ✅ Run the local demo
2. ✅ Test with different scenarios
3. ✅ Get Gemini API key for full AI features
4. ✅ (Optional) Deploy to Google Cloud Run
5. ✅ (Optional) Integrate real traffic data

---

## Key Features to Try

- 🤖 **AI Explanation:** Read the generated explanation for each prediction
- 🗺️ **Route Visualization:** Click and explore the route on the map
- 📊 **Risk Gauge:** See the delay probability visualized
- 📋 **Alternative Routes:** Compare ranked route options
- 💾 **History:** Load past shipment predictions from Firebase

---

## Performance Tips

- First prediction may take 2-3 seconds (model load)
- Subsequent predictions are <500ms
- Gemini explanation adds ~2-3 seconds first call
- Maps render instantly with Folium

---

## Support & Resources

- 📖 Code: See `CONFIG_GUIDE.md` for detailed setup
- 🚀 Deployment: See `DEPLOYMENT_GUIDE.md`
- 🎤 Presentation: See `PRESENTATION_GUIDE.md`
- 📚 API Docs: Visit http://localhost:8000/docs (while running)

---

**Happy shipping! 🚚** 

*Questions? Check CONFIG_GUIDE.md for detailed setup instructions.*
