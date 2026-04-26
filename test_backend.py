#!/usr/bin/env python
"""
Quick test to verify PASCI backend is working correctly.
Run this to test predictions without the frontend.
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("\n" + "="*60)
    print("🏥 TESTING HEALTH ENDPOINT")
    print("="*60)
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        if resp.status_code == 200:
            print("✅ PASS: Health check OK")
            print(f"   Response: {resp.json()}")
            return True
        else:
            print(f"❌ FAIL: Status {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def test_predict(distance, traffic, weather, description):
    """Test prediction endpoint."""
    print("\n" + "="*60)
    print(f"🚚 TEST: {description}")
    print("="*60)
    
    payload = {
        "distance": distance,
        "traffic": traffic,
        "weather": weather,
    }
    
    print(f"Input: Distance={distance}km, Traffic={traffic}, Weather={weather}")
    
    try:
        resp = requests.post(
            f"{API_URL}/predict",
            json=payload,
            timeout=10
        )
        
        if resp.status_code == 200:
            result = resp.json()
            print(f"✅ PASS: Prediction successful")
            print(f"\n   Risk: {result['risk_pct']}")
            print(f"   Status: {result['status']}")
            print(f"   Route: {' → '.join(result['route'])}")
            print(f"   Explanation: {result.get('explanation', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ FAIL: Status {resp.status_code}")
            print(f"   Error: {resp.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ FAIL: Cannot connect to API")
        print("   Make sure backend is running: python -m uvicorn backend.app:app --reload")
        return False
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("PASCI BACKEND TEST SUITE")
    print("="*60)
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    # Test scenarios
    results.append(("Low Risk", test_predict(150, 0, 0, "Low Risk (Clear, No Traffic)")))
    results.append(("Medium Risk", test_predict(250, 1, 1, "Medium Risk (Rain, Medium Traffic)")))
    results.append(("High Risk", test_predict(300, 2, 2, "High Risk (Storm, Heavy Traffic)")))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}  {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Backend is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Check logs above.")
        return 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
