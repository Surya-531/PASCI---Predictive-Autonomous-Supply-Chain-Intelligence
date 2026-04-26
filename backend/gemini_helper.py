"""
PASCI – Gemini AI Assistant
Provides explainable AI insights for logistics decisions.
Uses Google Generative AI (Gemini) to explain delay risks and route recommendations.
"""

import os
import google.generativeai as genai
from typing import Optional

# ── Configure Gemini API ──────────────────────────────────────────────────────
# Use environment variable first, fallback to default
API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBvWHdx7T4xmWWYZjlleS_vTbj41a6ohE0")

# Only configure if key is provided and not empty
if API_KEY and API_KEY.strip():
    try:
        genai.configure(api_key=API_KEY)
    except Exception as e:
        print(f"[gemini_helper] Warning: Could not configure Gemini API: {e}")
        API_KEY = None
else:
    API_KEY = None

MODEL = genai.GenerativeModel("gemini-pro") if API_KEY else None

# ── Traffic and weather mappings ──────────────────────────────────────────────
TRAFFIC_LABELS = {0: "Low", 1: "Medium", 2: "High"}
WEATHER_LABELS = {0: "Clear", 1: "Rain", 2: "Storm"}


def explain_prediction(
    risk: float,
    traffic: int,
    weather: int,
    route: list,
    distance: int,
) -> str:
    """
    Generate an AI-powered explanation for a shipment delay prediction.

    Args:
        risk (float):       Delay probability (0.0 to 1.0)
        traffic (int):      Traffic level (0=low, 1=medium, 2=high)
        weather (int):      Weather condition (0=clear, 1=rain, 2=storm)
        route (list):       List of cities in the optimised route
        distance (int):     Distance in km

    Returns:
        str: Human-readable explanation from Gemini or fallback.
    """
    if not API_KEY or not MODEL:
        # Fallback explanation if Gemini not available
        return _generate_fallback_explanation(risk, traffic, weather, route, distance)
    
    traffic_label = TRAFFIC_LABELS.get(traffic, "Unknown")
    weather_label = WEATHER_LABELS.get(weather, "Unknown")
    route_str = " → ".join(route)
    risk_pct = risk * 100

    # Determine risk level
    if risk_pct >= 70:
        risk_level = "HIGH"
    elif risk_pct >= 40:
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"

    prompt = f"""
    You are a logistics AI assistant for PASCI (Predictive Autonomous Supply Chain Intelligence).
    
    Analyze the following shipment conditions and provide a brief, actionable explanation:
    
    **Shipment Details:**
    - Distance: {distance} km
    - Traffic Level: {traffic_label}
    - Weather Condition: {weather_label}
    - Delay Risk Level: {risk_level} ({risk_pct:.1f}%)
    - Suggested Route: {route_str}
    
    **Your task:**
    1. Explain WHY this delay risk exists (focus on traffic and weather factors)
    2. Explain WHY the suggested route is optimal given these conditions
    3. Provide 1-2 short, actionable recommendations
    
    Keep the response concise (3-4 sentences max), professional, and action-oriented.
    Format as plain text, no markdown.
    """

    try:
        response = MODEL.generate_content(prompt, timeout=10)
        explanation = response.text.strip()
        return explanation
    except Exception as e:
        print(f"[gemini_helper] Error calling Gemini API: {e}")
        # Fallback to templated explanation
        return _generate_fallback_explanation(risk, traffic, weather, route, distance)


def _generate_fallback_explanation(
    risk: float,
    traffic: int,
    weather: int,
    route: list,
    distance: int,
) -> str:
    """Generate a templated explanation when Gemini is unavailable."""
    traffic_label = TRAFFIC_LABELS.get(traffic, "Unknown")
    weather_label = WEATHER_LABELS.get(weather, "Unknown")
    route_str = " → ".join(route)
    risk_pct = risk * 100
    
    if risk_pct >= 70:
        risk_desc = "HIGH"
        action = "Consider rerouting or delaying the shipment"
    elif risk_pct >= 40:
        risk_desc = "MEDIUM"
        action = "Monitor conditions and be prepared to adapt"
    else:
        risk_desc = "LOW"
        action = "Proceed as scheduled"
    
    return (
        f"Delay risk is {risk_desc} ({risk_pct:.0f}%) due to {traffic_label} traffic "
        f"and {weather_label} weather conditions. "
        f"The route {route_str} is optimized to minimize delays. "
        f"{action}."
    )


def get_alternative_recommendations(
    risk: float,
    traffic: int,
    weather: int,
    route: list,
) -> str:
    """
    Generate strategic recommendations for risk mitigation.

    Args:
        risk (float):       Delay probability
        traffic (int):      Traffic level
        weather (int):      Weather condition
        route (list):       Optimised route

    Returns:
        str: Risk mitigation recommendations.
    """
    traffic_label = TRAFFIC_LABELS.get(traffic, "Unknown")
    weather_label = WEATHER_LABELS.get(weather, "Unknown")
    route_str = " → ".join(route)

    prompt = f"""
    You are a supply chain strategy advisor.
    
    Given:
    - Traffic: {traffic_label}
    - Weather: {weather_label}
    - Current Route: {route_str}
    - Delay Risk: {risk * 100:.1f}%
    
    Provide 2-3 strategic recommendations to reduce delay risk:
    1. Operational changes
    2. Route adjustments
    3. Contingency planning
    
    Format as a numbered list. Keep each point to 1 sentence.
    """

    try:
        response = MODEL.generate_content(prompt)
        recommendations = response.text.strip()
        return recommendations
    except Exception as e:
        print(f"[gemini_helper] Error calling Gemini API: {e}")
        return "Unable to generate recommendations at this time."


if __name__ == "__main__":
    # Quick test
    test_explanation = explain_prediction(
        risk=0.82,
        traffic=2,
        weather=2,
        route=["Chennai", "Salem", "Bangalore"],
        distance=300,
    )
    print("Explanation:", test_explanation)

    test_recommendations = get_alternative_recommendations(
        risk=0.82,
        traffic=2,
        weather=2,
        route=["Chennai", "Salem", "Bangalore"],
    )
    print("\nRecommendations:", test_recommendations)
