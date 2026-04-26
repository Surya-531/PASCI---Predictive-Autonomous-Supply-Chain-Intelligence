# PASCI Configuration Guide

## Environment Variables

This document explains how to configure API keys and other settings for the PASCI system.

### 1. Gemini API Key (Required)

The AI Logistics Assistant requires a Google Generative AI API key for the Gemini model.

**Setup:**

```bash
# Option 1: Set as environment variable (Linux/Mac)
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Option 2: Set as environment variable (Windows PowerShell)
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"

# Option 3: Create a .env file in the project root (recommended for development)
# Add this line to .env:
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

**Get your API Key:**

1. Visit: https://aistudio.google.com/
2. Click "Create API Key"
3. Copy the key
4. Set it as shown above

**Currently configured key:** The default key in `backend/gemini_helper.py` is used if the environment variable is not set.

### 2. Google Maps API Key (Optional)

For Google Maps route visualization, you can optionally set a Google Maps API key.

**Setup:**

```bash
# Option 1: Set as environment variable (Linux/Mac)
export GOOGLE_MAPS_API_KEY="YOUR_MAPS_API_KEY"

# Option 2: Set as environment variable (Windows PowerShell)
$env:GOOGLE_MAPS_API_KEY="YOUR_MAPS_API_KEY"

# Option 3: Add to .env file
GOOGLE_MAPS_API_KEY=YOUR_MAPS_API_KEY
```

**Get your API Key:**

1. Visit: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable APIs:
   - Maps JavaScript API
   - Directions API
4. Create API key (Credentials → Create Credentials → API Key)
5. Restrict key to HTTP referrers
6. Copy the key

**Note:** If not set, the app will use Folium maps (open-source alternative).

### 3. Firebase Configuration

Firebase is used for data persistence. Configuration file: `serviceAccountKey.json`

See `firebase/firebase_config.py` for setup details.

## Installation & Running

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Train the Model

```bash
python model/generate_data.py
python model/train_model.py
```

### 3. Run the Backend API

```bash
python -m uvicorn backend.app:app --host 0.0.0.0 --port 8000 --reload
```

### 4. Run the Frontend (in another terminal)

```bash
streamlit run frontend/app.py
```

The frontend will be available at: http://localhost:8501

## Testing

### Test Gemini Integration

```bash
python backend/gemini_helper.py
```

This will generate an explanation for a sample shipment.

### Test with curl (API)

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 300,
    "traffic": 2,
    "weather": 2
  }'
```

## Deployment to Google Cloud

### Option 1: Cloud Run (Recommended)

```bash
# Initialize Google Cloud
gcloud init

# Build Docker image
gcloud run deploy pasci-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=YOUR_KEY

# Frontend: Deploy to Cloud Run as well
gcloud run deploy pasci-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 2: Firebase Hosting + Cloud Run

- Backend: Deploy to Cloud Run (as shown above)
- Frontend: Build Streamlit and deploy to Firebase Hosting

## Architecture Overview

```
Frontend (Streamlit)
    ↓
FastAPI Backend
    ↓
ML Model (Random Forest)
    ↓
Route Optimizer (Dijkstra)
    ↓
Gemini AI (Explanation)
    ↓
Firebase (Storage)
    ↓
Google Cloud Run (Deployment)
```

## Features

✅ **ML Prediction:** Random Forest model predicts delay risk
✅ **Route Optimization:** Dijkstra algorithm finds optimal routes
✅ **AI Explanation:** Gemini provides human-readable explanations
✅ **Route Visualization:** Interactive maps (Folium + Google Maps)
✅ **Data Persistence:** Firebase Firestore integration
✅ **Cloud Ready:** Deploy to Google Cloud Run

## Troubleshooting

### Gemini API returns 429 error
- Rate limit exceeded. Wait a moment and retry.
- Consider upgrading your API quota.

### Maps not displaying
- Ensure folium and streamlit-folium are installed
- Check that city names match those in CITY_COORDS dictionary

### Firebase connection fails
- Verify serviceAccountKey.json is present
- Check Firebase credentials
- Ensure internet connection

### Model not found
- Run: `python model/generate_data.py && python model/train_model.py`
- Check that `model/model.pkl` exists

## Support

For issues or questions, refer to:
- Gemini API Docs: https://ai.google.dev/
- Streamlit Docs: https://docs.streamlit.io/
- FastAPI Docs: https://fastapi.tiangolo.com/
