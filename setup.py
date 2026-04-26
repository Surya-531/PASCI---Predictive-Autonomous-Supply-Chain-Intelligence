#!/usr/bin/env python3
"""
PASCI – One-shot setup script
Generates synthetic data and trains ALL ML models.
Run once before starting the API server.

Usage:
    python setup.py
"""

import os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

print("=" * 60)
print("  PASCI – Setup Script")
print("=" * 60)

# Step 1: Generate dataset
print("\n[1/2] Generating synthetic dataset ...")
from model.generate_data import generate_dataset
generate_dataset(save_path=os.path.join(ROOT, "data", "data.csv"))

# Step 2: Train all models
print("\n[2/2] Training all ML models ...")
from model.train_model import train_all
train_all()

print("\n" + "=" * 60)
print("  Setup complete! Files created:")
print("=" * 60)

for fname in [
    "data/data.csv",
    "model/model.pkl",
    "model/gradient_boost.pkl",
    "model/logistic.pkl",
    "model/knn.pkl",
    "model/scaler.pkl",
    "model/evaluation_report.txt",
]:
    full = os.path.join(ROOT, fname)
    size = os.path.getsize(full) if os.path.exists(full) else 0
    tick = "OK" if os.path.exists(full) else "MISSING"
    print(f"  [{tick}] {fname:<40} {size:>8} bytes")

print("\nNext steps:")
print("  Start API  ->  uvicorn backend.app:app --reload")
print("  Start UI   ->  streamlit run frontend/app.py")
