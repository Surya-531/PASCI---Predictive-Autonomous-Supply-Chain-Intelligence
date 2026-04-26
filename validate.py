#!/usr/bin/env python
"""
PASCI – Quick Validation Script
Verifies all components are working correctly.
"""

import sys
import os

# Add project to path
ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT)

def test_imports():
    """Test that all required modules can be imported."""
    print("✓ Testing imports...")
    try:
        from backend.app import app, PredictRequest, PredictResponse
        print("  ✓ Backend app imports OK")
    except Exception as e:
        print(f"  ✗ Backend app import failed: {e}")
        return False

    try:
        from backend.gemini_helper import explain_prediction
        print("  ✓ Gemini helper imports OK")
    except Exception as e:
        print(f"  ✗ Gemini helper import failed: {e}")
        return False

    try:
        from optimization.route_optimizer import get_best_route, get_all_routes
        print("  ✓ Route optimizer imports OK")
    except Exception as e:
        print(f"  ✗ Route optimizer import failed: {e}")
        return False

    try:
        import streamlit as st
        print("  ✓ Streamlit imports OK")
    except Exception as e:
        print(f"  ✗ Streamlit import failed: {e}")
        return False

    try:
        import folium
        print("  ✓ Folium imports OK")
    except Exception as e:
        print(f"  ✗ Folium import failed: {e}")
        return False

    try:
        import google.generativeai as genai
        print("  ✓ Google Generative AI imports OK")
    except Exception as e:
        print(f"  ✗ Google Generative AI import failed: {e}")
        return False

    return True


def test_model_exists():
    """Check if the model file exists."""
    print("\n✓ Checking model file...")
    model_path = os.path.join(ROOT, "model", "model.pkl")
    if os.path.exists(model_path):
        size_mb = os.path.getsize(model_path) / (1024 * 1024)
        print(f"  ✓ Model file exists ({size_mb:.2f} MB)")
        return True
    else:
        print(f"  ✗ Model file not found at {model_path}")
        print("    Run: python model/generate_data.py && python model/train_model.py")
        return False


def test_route_optimizer():
    """Test route optimization functionality."""
    print("\n✓ Testing route optimizer...")
    try:
        from optimization.route_optimizer import get_best_route, get_all_routes

        # Test with various scenarios
        scenarios = [
            (0, 0, "clear/no traffic"),
            (2, 2, "storm/heavy traffic"),
            (1, 1, "rain/medium traffic"),
        ]

        for traffic, weather, desc in scenarios:
            route = get_best_route(traffic, weather)
            routes = get_all_routes(traffic, weather)
            print(f"  ✓ {desc:25s} → {' → '.join(route)} ({len(routes)} routes available)")

        return True
    except Exception as e:
        print(f"  ✗ Route optimizer test failed: {e}")
        return False


def test_gemini_integration():
    """Test Gemini integration."""
    print("\n✓ Testing Gemini integration...")
    try:
        from backend.gemini_helper import explain_prediction

        # Test with sample data
        explanation = explain_prediction(
            risk=0.75,
            traffic=2,
            weather=2,
            route=["Chennai", "Salem", "Bangalore"],
            distance=300,
        )

        if explanation and len(explanation) > 10:
            print(f"  ✓ Gemini explanation generated ({len(explanation)} chars)")
            print(f"    Preview: {explanation[:100]}...")
            return True
        else:
            print("  ✗ Gemini returned empty explanation")
            return False
    except Exception as e:
        print(f"  ✗ Gemini test failed: {e}")
        print("    (This is OK if API key is not set or network unavailable)")
        return False


def test_api_models():
    """Test FastAPI request/response models."""
    print("\n✓ Testing API models...")
    try:
        from backend.app import PredictRequest, PredictResponse

        # Test request
        req = PredictRequest(
            shipment_id="TEST001",
            distance=300,
            traffic=1,
            weather=1,
        )
        print(f"  ✓ PredictRequest model OK ({req.shipment_id})")

        # Test response
        resp = PredictResponse(
            shipment_id="TEST001",
            delay=1,
            risk=0.75,
            risk_pct="75.0%",
            status="HIGH RISK",
            route=["Chennai", "Salem", "Bangalore"],
            all_routes=[],
            alert=True,
            alert_msg="High risk",
            timestamp="2025-01-01T00:00:00",
            firebase_doc="test-doc",
            explanation="Test explanation",
        )
        print(f"  ✓ PredictResponse model OK (risk={resp.risk_pct})")
        return True
    except Exception as e:
        print(f"  ✗ API models test failed: {e}")
        return False


def test_dependencies():
    """Check all required dependencies are installed."""
    print("\n✓ Checking dependencies...")
    required = [
        "fastapi",
        "uvicorn",
        "pydantic",
        "streamlit",
        "scikit-learn",
        "pandas",
        "numpy",
        "joblib",
        "networkx",
        "requests",
        "folium",
        "google.generativeai",
    ]

    missing = []
    for package in required:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)

    if missing:
        print(f"  ✗ Missing packages: {', '.join(missing)}")
        print("    Run: pip install -r requirements.txt")
        return False
    else:
        print(f"  ✓ All {len(required)} dependencies installed")
        return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("PASCI – Validation Script")
    print("=" * 60)

    results = []

    # Run tests
    results.append(("Dependencies", test_dependencies()))
    results.append(("Imports", test_imports()))
    results.append(("Model File", test_model_exists()))
    results.append(("API Models", test_api_models()))
    results.append(("Route Optimizer", test_route_optimizer()))
    results.append(("Gemini Integration", test_gemini_integration()))

    # Summary
    print("\n" + "=" * 60)
    print("VALIDATION SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:8s} {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All systems operational! Ready to run PASCI.")
        print("\nNext steps:")
        print("  1. Terminal 1: python -m uvicorn backend.app:app --reload")
        print("  2. Terminal 2: streamlit run frontend/app.py")
        print("  3. Visit: http://localhost:8501")
        return 0
    else:
        print("\n⚠️  Some tests failed. See above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
