"""
PASCI – Firebase Integration Module
Initialises Firebase Admin SDK and provides helper functions to store
and retrieve shipment predictions from Firestore.

SETUP:
    1. Go to https://console.firebase.google.com/
    2. Create a project → Project Settings → Service Accounts
    3. Click "Generate new private key" → store its JSON content in FIREBASE_KEY
"""

import os
import json
from datetime import datetime, timezone
from typing import Optional

# ---------------------------------------------------------------------------
# Lazy initialisation – we import firebase_admin only when available so the
# rest of the app can still run without a real Firebase key (demo / CI mode).
# ---------------------------------------------------------------------------
_db: Optional[object] = None
_FIREBASE_AVAILABLE = False

def _init_firebase():
    """Initialise Firebase once; return Firestore client or None."""
    global _db, _FIREBASE_AVAILABLE

    if _db is not None:
        return _db

    if "FIREBASE_KEY" not in os.environ:
        print(
            "[firebase] WARNING: FIREBASE_KEY environment variable not found. "
            "Running in DEMO mode – results will NOT be persisted to Firebase."
        )
        return None

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore

        if not firebase_admin._apps:
            firebase_json = json.loads(os.environ["FIREBASE_KEY"])
            cred = credentials.Certificate(firebase_json)
            firebase_admin.initialize_app(cred)

        _db = firestore.client()
        _FIREBASE_AVAILABLE = True
        print("[firebase] Connected to Firestore ✅")
        return _db

    except Exception as exc:
        print(f"[firebase] Could not connect: {exc}")
        return None


def save_shipment(result: dict) -> str:
    """
    Persist a prediction result to the 'shipments' Firestore collection.

    Args:
        result: {
            "shipment_id": str,
            "delay":       0 | 1,
            "risk":        float,
            "route":       list[str],
        }

    Returns:
        Firestore document ID, or "demo-mode" if Firebase is unavailable.
    """
    db = _init_firebase()

    payload = {
        **result,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    if db is None:
        # Demo mode: just print
        print(f"[firebase][DEMO] Would save: {json.dumps(payload, indent=2)}")
        return "demo-mode"

    from firebase_admin import firestore as _fs  # noqa: F811
    doc_ref = db.collection("shipments").add(payload)
    doc_id  = doc_ref[1].id
    print(f"[firebase] Saved shipment → doc_id={doc_id}")
    return doc_id


def get_recent_shipments(limit: int = 10) -> list:
    """
    Retrieve the most recent shipment predictions from Firestore.

    Returns:
        List of dicts (empty list if Firebase unavailable).
    """
    db = _init_firebase()
    if db is None:
        return []

    docs = (
        db.collection("shipments")
        .order_by("timestamp", direction="DESCENDING")
        .limit(limit)
        .stream()
    )
    return [{"id": d.id, **d.to_dict()} for d in docs]
