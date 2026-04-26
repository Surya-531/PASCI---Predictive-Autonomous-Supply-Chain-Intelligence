# PASCI Deployment Guide – Google Cloud Run

This guide shows how to deploy PASCI to Google Cloud Run for production.

## Prerequisites

- Google Cloud Account (with billing enabled)
- `gcloud` CLI installed: https://cloud.google.com/sdk/docs/install
- Docker installed (optional, Cloud Run can build from source)
- Git

## Step 1: Authenticate with Google Cloud

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
```

Replace `YOUR_PROJECT_ID` with your actual Google Cloud project ID.

## Step 2: Create Dockerfile for Backend

Create a file named `Dockerfile` in the project root:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run FastAPI server
CMD ["python", "-m", "uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Step 3: Set Environment Variables

Create a `.env.prod` file (do NOT commit to GitHub):

```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
GOOGLE_MAPS_API_KEY=YOUR_MAPS_API_KEY
FIREBASE_PROJECT_ID=YOUR_FIREBASE_PROJECT_ID
```

## Step 4: Deploy Backend to Cloud Run

```bash
# Build and deploy in one command
gcloud run deploy pasci-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --timeout 3600 \
  --set-env-vars \
    GEMINI_API_KEY="YOUR_GEMINI_API_KEY",\
    GOOGLE_MAPS_API_KEY="YOUR_MAPS_API_KEY"
```

**Expected Output:**
```
Service [pasci-api] has been successfully deployed.
Service URL: https://pasci-api-xxxxxxxx-uc.a.run.app
```

## Step 5: Deploy Frontend to Cloud Run

Create `Dockerfile.frontend`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y build-essential && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "frontend/app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.enableXsrfProtection=false"]
```

Deploy frontend:

```bash
gcloud run deploy pasci-frontend \
  --source . \
  --dockerfile Dockerfile.frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --set-env-vars \
    PASCI_API_URL="https://pasci-api-xxxxxxxx-uc.a.run.app"
```

Replace the URL with the backend API URL from Step 4.

## Step 6: Configure CORS (if needed)

If frontend and backend are on different Cloud Run services, ensure CORS is configured in `backend/app.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

This is already configured in the current app.py.

## Step 7: Monitor Deployment

```bash
# View logs
gcloud run logs read pasci-api --limit 100

# View metrics
gcloud run services describe pasci-api --region us-central1

# Set custom domain (optional)
gcloud run services update-traffic pasci-api --update-routes
```

## Step 8: Set Up CI/CD (GitHub Actions)

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Cloud Run

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Cloud SDK
      uses: google-github-actions/setup-gcloud@v1
      with:
        service_account_key: ${{ secrets.GCP_SA_KEY }}
        project_id: ${{ secrets.GCP_PROJECT_ID }}
    
    - name: Deploy Backend
      run: |
        gcloud run deploy pasci-api \
          --source . \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated \
          --set-env-vars \
            GEMINI_API_KEY="${{ secrets.GEMINI_API_KEY }}"
    
    - name: Deploy Frontend
      run: |
        gcloud run deploy pasci-frontend \
          --source . \
          --dockerfile Dockerfile.frontend \
          --platform managed \
          --region us-central1 \
          --allow-unauthenticated
```

### Add Secrets to GitHub

1. Go to repo Settings → Secrets and Variables → Actions
2. Add:
   - `GCP_PROJECT_ID`
   - `GCP_SA_KEY` (service account JSON)
   - `GEMINI_API_KEY`
   - `GOOGLE_MAPS_API_KEY`

## Step 9: Verify Deployment

### Test Backend

```bash
curl https://pasci-api-xxxxxxxx-uc.a.run.app/health
```

Expected response:
```json
{"status": "ok", "service": "PASCI API"}
```

### Test Prediction

```bash
curl -X POST https://pasci-api-xxxxxxxx-uc.a.run.app/predict \
  -H "Content-Type: application/json" \
  -d '{
    "distance": 300,
    "traffic": 2,
    "weather": 2
  }'
```

### Access Frontend

Visit: `https://pasci-frontend-xxxxxxxx-uc.a.run.app`

## Optimization Tips

### Reduce Cold Start Time

1. Use smaller base images (slim, alpine)
2. Pre-warm instances: Set min instances to 1
   ```bash
   gcloud run services update pasci-api \
     --min-instances 1 \
     --region us-central1
   ```

3. Optimize dependencies - remove unused packages

### Cost Optimization

- Use `--memory 256Mi` for lightweight services
- Enable autoscaling: `--max-instances 10`
- Schedule scale-down during off-hours

### Monitoring

Enable Google Cloud Monitoring:

```bash
gcloud run services describe pasci-api \
  --region us-central1 \
  --format='value(status.url)'
```

## Rollback Deployment

```bash
# Rollback to previous version
gcloud run services update-traffic pasci-api \
  --to-revisions LATEST=0,PREVIOUS=100 \
  --region us-central1
```

## Troubleshooting

### 502 Bad Gateway

- Check service logs: `gcloud run logs read pasci-api`
- Ensure environment variables are set correctly
- Verify Dockerfile is correct

### Timeout Error

- Increase timeout: `--timeout 3600`
- Check if external APIs (Gemini, Firebase) are slow

### Out of Memory

- Increase memory: `--memory 1Gi`
- Profile app for memory leaks

## Cost Estimate (Monthly)

- Cloud Run compute: ~$1-5 (with free tier)
- API calls (Gemini): ~$0-50 depending on usage
- Firebase (Firestore): ~$0-10 depending on usage
- Total: ~$10-30/month for prototype

## Next Steps

1. ✅ Deploy both services
2. ✅ Configure domain name (optional)
3. ✅ Set up monitoring & alerts
4. ✅ Enable Cloud Storage for logs
5. ✅ Add Cloud SQL for advanced analytics

## Resources

- Cloud Run: https://cloud.google.com/run/docs
- Pricing: https://cloud.google.com/run/pricing
- CLI Reference: https://cloud.google.com/cli/docs
- Troubleshooting: https://cloud.google.com/run/docs/troubleshooting

---

**Your PASCI system is now production-ready!** 🚀
