"""
PASCI – FastAPI Backend
Exposes:
    POST /predict      – predict delay risk + suggest route
    GET  /history      – retrieve recent shipments from Firebase
    GET  /health       – health-check
"""

import os
import sys
import uuid
from datetime import datetime, timezone

import joblib
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Path setup so sibling packages resolve correctly ──────────────────────────
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from optimization.route_optimizer import get_best_route, get_all_routes  # noqa: E402
from firebase.firebase_config import save_shipment, get_recent_shipments  # noqa: E402
from backend.gemini_helper import explain_prediction  # noqa: E402

# ── Model path ────────────────────────────────────────────────────────────────
MODEL_PATH = os.path.join(ROOT, "model", "model.pkl")

# ── FastAPI app ───────────────────────────────────────────────────────────────
app = FastAPI(
    title="PASCI – Predictive Autonomous Supply Chain Intelligence",
    description="Predicts shipment delays and suggests optimised routes.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Lazy model loader ─────────────────────────────────────────────────────────
_model = None


@app.on_event("startup")
def startup_event():
    """Preload the model when FastAPI starts so the first /predict call is fast."""
    try:
        _get_model()
    except HTTPException as exc:
        print(f"[startup] Model not loaded: {exc.detail}")

def _get_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise HTTPException(
                status_code=503,
                detail=(
                    "Model not found. "
                    "Run: python model/generate_data.py && python model/train_model.py"
                ),
            )
        _model = joblib.load(MODEL_PATH)
    return _model


# ── Request / Response schemas ────────────────────────────────────────────────
class PredictRequest(BaseModel):
    shipment_id : str = Field(default_factory=lambda: f"S{uuid.uuid4().hex[:6].upper()}")
    distance    : int = Field(..., ge=50, le=500,  description="Distance in km (50–500)")
    traffic     : int = Field(..., ge=0,  le=2,    description="0=low | 1=medium | 2=high")
    weather     : int = Field(..., ge=0,  le=2,    description="0=clear | 1=rain | 2=storm")
    source      : str = Field(default="Chennai",   description="Source city")
    destination : str = Field(default="Bangalore", description="Destination city")


class RouteInfo(BaseModel):
    route : list[str]
    cost  : float
    base_distance : float = 0.0
    risk_adjusted_cost : float = 0.0


class PredictResponse(BaseModel):
    shipment_id   : str
    delay         : int
    risk          : float
    risk_pct      : str
    status        : str
    route         : list[str]
    all_routes    : list[RouteInfo]
    alert         : bool
    alert_msg     : str
    timestamp     : str
    firebase_doc  : str
    explanation   : str = ""  # AI-generated explanation from Gemini


# ── Endpoints ─────────────────────────────────────────────────────────────────
@app.get("/health")
def health():
    return {"status": "ok", "service": "PASCI API"}


@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    """
    Predict delay risk and return optimised route.

    - Loads trained RandomForest model
    - Runs Dijkstra-based route optimisation with risk-adjusted weights
    - Persists result to Firebase
    - Triggers alert if risk > 70 %
    """
    clf = _get_model()

    # ── ML prediction ─────────────────────────────────────────────────────────
    import pandas as _pd
    X      = _pd.DataFrame(
        [[req.distance, req.traffic, req.weather]],
        columns=["distance", "traffic", "weather"],
    )
    delay  = int(clf.predict(X)[0])
    risk   = round(float(clf.predict_proba(X)[0][1]), 4)

    # ── Route optimisation ────────────────────────────────────────────────────
    best_route = get_best_route(req.traffic, req.weather, source=req.source, destination=req.destination)
    all_routes = get_all_routes(req.traffic, req.weather, source=req.source, destination=req.destination)

    # ── AI explanation (Gemini) ───────────────────────────────────────────────
    try:
        explanation = explain_prediction(
            risk=risk,
            traffic=req.traffic,
            weather=req.weather,
            route=best_route,
            distance=req.distance,
            source=req.source,
            destination=req.destination,
        )
    except Exception as exc:
        print(f"[predict] Gemini explanation failed: {exc}")
        explanation = "AI explanation unavailable"

    # ── Alert logic ───────────────────────────────────────────────────────────
    alert     = risk > 0.70
    alert_msg = (
        f"⚠️  ALERT: Shipment {req.shipment_id} has HIGH delay risk ({risk*100:.1f}%)! "
        f"Suggested route: {' → '.join(best_route)}"
        if alert else ""
    )
    if alert:
        print(alert_msg)

    status = "HIGH RISK" if delay == 1 else "LOW RISK"

    result = {
        "shipment_id" : req.shipment_id,
        "delay"       : delay,
        "risk"        : risk,
        "route"       : best_route,
        "timestamp"   : datetime.now(timezone.utc).isoformat(),
    }

    # ── Firebase persistence ──────────────────────────────────────────────────
    try:
        doc_id = save_shipment(result)
    except Exception as exc:
        print(f"[predict] Firebase save failed: {exc}")
        doc_id = "demo-mode"

    return PredictResponse(
        shipment_id  = req.shipment_id,
        delay        = delay,
        risk         = risk,
        risk_pct     = f"{risk * 100:.1f}%",
        status       = status,
        route        = best_route,
        all_routes   = [RouteInfo(**r) for r in all_routes],
        alert        = alert,
        alert_msg    = alert_msg,
        timestamp    = result["timestamp"],
        firebase_doc = doc_id,
        explanation  = explanation,
    )


@app.get("/history")
def history(limit: int = 10):
    """Return the last N shipment predictions stored in Firebase."""
    records = get_recent_shipments(limit=limit)
    return {"count": len(records), "shipments": records}


# ── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="0.0.0.0", port=8000, reload=True)
