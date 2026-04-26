"""
PASCI â€“ Streamlit Frontend Dashboard
Connects to the FastAPI backend and provides an interactive UI for:
    - Inputting shipment parameters
    - Viewing delay risk predictions
    - Seeing the optimised route
    - Viewing alerts
    - (Optional) Shipment history from Firebase
"""

import os
import sys
import requests
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# Add the project root to the path for shared frontend utilities.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

API_URL = os.getenv(
    "PASCI_API_URL",
    "https://pasci--predictive-autonomous-supply-chain-l34j.onrender.com/predict",
)
API_BASE_URL = API_URL.removesuffix("/predict")

# â”€â”€ Page config â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.set_page_config(
    page_title="PASCI Dashboard",
    page_icon="ðŸšš",
    layout="wide",
)

# â”€â”€ Custom CSS â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.markdown(
    """
    <style>
        .big-metric { font-size: 2.5rem; font-weight: bold; }
        .risk-high  { color: #e74c3c; }
        .risk-low   { color: #2ecc71; }
        .route-box  {
            background: #1e1e2e;
            border-radius: 8px;
            padding: 12px 20px;
            font-size: 1.1rem;
            letter-spacing: 1px;
        }
        .explanation-box {
            background: linear-gradient(135deg, #1e3a8a 0%, #1e40af 100%);
            border-left: 5px solid #0ea5e9;
            border-radius: 8px;
            padding: 16px 20px;
            margin: 12px 0;
            font-size: 0.95rem;
            line-height: 1.8;
            color: #e0f2fe;
            box-shadow: 0 4px 6px rgba(14, 165, 233, 0.1);
            max-height: 600px;
            overflow-y: auto;
        }
        .explanation-box::-webkit-scrollbar {
            width: 6px;
        }
        .explanation-box::-webkit-scrollbar-track {
            background: rgba(14, 165, 233, 0.1);
            border-radius: 3px;
        }
        .explanation-box::-webkit-scrollbar-thumb {
            background: #0ea5e9;
            border-radius: 3px;
        }
        .explanation-box::-webkit-scrollbar-thumb:hover {
            background: #06b6d4;
        }
        .explanation-title {
            color: #0ea5e9;
            font-weight: bold;
            font-size: 1.1rem;
            margin-bottom: 8px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# â”€â”€ Map visualization functions â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
# City coordinates for Folium maps
CITY_COORDS = {
    "Chennai": [13.0827, 80.2707],
    "Vellore": [12.9165, 79.1325],
    "Salem": [11.6643, 78.1460],
    "Bangalore": [12.9716, 77.5946],
    "Krishnagiri": [12.2033, 78.9108],
}


def generate_detailed_explanation(result: dict, distance: int, traffic: int, weather: int) -> str:
    """
    Generate a detailed AI explanation for the prediction result.
    
    Args:
        result (dict): The prediction result
        distance (int): Distance in km
        traffic (int): Traffic level (0=Low, 1=Medium, 2=High)
        weather (int): Weather condition (0=Clear, 1=Rain, 2=Storm)
    
    Returns:
        str: Detailed HTML explanation
    """
    traffic_names = {0: "Low", 1: "Medium", 2: "High"}
    weather_names = {0: "Clear", 1: "Rain", 2: "Storm"}
    
    risk_level = result["risk"]
    delay_hours = result["delay"]
    route_str = " â†’ ".join(result["route"])
    traffic_name = traffic_names.get(traffic, "Unknown")
    weather_name = weather_names.get(weather, "Unknown")
    
    # Generate detailed explanation based on risk level and conditions
    if risk_level > 0.7:
        risk_assessment = "<strong>CRITICAL RISK:</strong> This shipment has a very high probability of experiencing delays."
        recommendation = "Consider immediate action: reroute, delay departure, or expedite with premium service."
    elif risk_level > 0.4:
        risk_assessment = "<strong>MODERATE RISK:</strong> There is a reasonable chance of delays under current conditions."
        recommendation = "Monitor the shipment closely and have contingency plans ready."
    else:
        risk_assessment = "<strong>LOW RISK:</strong> This shipment is well-positioned for on-time delivery."
        recommendation = "Proceed with standard operations, but continue monitoring for unexpected changes."
    
    explanation = f"""
    <div class="explanation-title">ðŸ“Š Detailed Analysis & Recommendations</div>
    <p><strong>Current Conditions:</strong></p>
    <ul>
        <li><strong>Distance:</strong> {distance} km</li>
        <li><strong>Traffic Level:</strong> {traffic_name}</li>
        <li><strong>Weather Condition:</strong> {weather_name}</li>
        <li><strong>Delay Risk:</strong> {risk_level*100:.1f}%</li>
        <li><strong>Estimated Delay:</strong> {delay_hours} hour(s)</li>
    </ul>
    <p><strong>Risk Assessment:</strong><br>{risk_assessment}</p>
    <p><strong>Optimized Route:</strong> {route_str}</p>
    <p><strong>Why This Route?</strong> This route has been optimized using Dijkstra's algorithm with dynamic penalties for traffic and weather conditions. It minimizes total travel time and risk factors.</p>
    <p><strong>AI Recommendations:</strong><br>{recommendation}</p>
    <p><strong>Key Factors Affecting This Prediction:</strong></p>
    <ul>
        <li>{'ðŸš¨ Heavy traffic conditions may cause significant delays' if traffic == 2 else 'âœ… Traffic conditions are favorable' if traffic == 0 else 'âš ï¸ Moderate traffic may add some travel time'}</li>
        <li>{'â›ˆ Severe weather (storm) may impact road safety and speed' if weather == 2 else 'â˜€ï¸ Clear weather supports smooth transit' if weather == 0 else 'ðŸŒ§ Rain may reduce speeds and increase travel time'}</li>
        <li>{'ðŸ“ Long distance increases exposure to cumulative delays' if distance > 300 else 'ðŸ“ Moderate distance is manageable' if distance > 150 else 'ðŸ“ Short distance minimizes delay risks'}</li>
    </ul>
    """
    return explanation


def show_map_google(route: list, api_key: str = None) -> None:
    """
    Display route using Google Maps Embed API.
    
    Args:
        route (list): List of cities in the route
        api_key (str): Google Maps API key
    """
    if not route or len(route) < 2:
        st.warning("Route must have at least 2 cities.")
        return

    origin = route[0]
    destination = route[-1]

    if len(route) > 2:
        waypoints = "|".join(route[1:-1])
        map_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}&waypoints={waypoints}&mode=driving"
    else:
        map_url = f"https://www.google.com/maps/embed/v1/directions?key={api_key}&origin={origin}&destination={destination}&mode=driving"

    if api_key:
        st.components.v1.iframe(src=map_url, height=500, scrolling=False)
    else:
        st.info("â„¹ï¸ Google Maps API key not configured. Use Folium visualization instead.")


def show_map_folium(route: list) -> None:
    """
    Display route using Folium interactive map.
    
    Args:
        route (list): List of cities in the route
    """
    if not route or len(route) < 2:
        st.warning("Route must have at least 2 cities.")
        return

    # Get starting coordinates
    start_city = route[0]
    if start_city not in CITY_COORDS:
        st.error(f"City '{start_city}' not found in coordinates database.")
        return

    start_coords = CITY_COORDS[start_city]

    # Create map
    m = folium.Map(
        location=start_coords,
        zoom_start=6,
        tiles="OpenStreetMap"
    )

    # Extract route coordinates
    route_coords = []
    for city in route:
        if city in CITY_COORDS:
            coord = CITY_COORDS[city]
            route_coords.append(coord)
            # Add marker
            folium.Marker(
                location=coord,
                popup=city,
                tooltip=city,
                icon=folium.Icon(color="blue", icon="info-sign")
            ).add_to(m)
        else:
            st.warning(f"City '{city}' coordinates not available.")

    # Draw polyline for route
    if len(route_coords) >= 2:
        folium.PolyLine(
            locations=route_coords,
            color="red",
            weight=3,
            opacity=0.8
        ).add_to(m)

    # Display map
    st_folium(m, width=700, height=500)

# â”€â”€ Title â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
st.title("ðŸšš PASCI â€“ Predictive Autonomous Supply Chain Intelligence")
st.caption("Real-time shipment delay prediction & route optimisation")
st.divider()

# â”€â”€ Sidebar â€“ Input form â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with st.sidebar:
    st.header("ðŸ“¦ Shipment Input")

    shipment_id = st.text_input("Shipment ID", value="S101", max_chars=20)

    # â”€â”€ Route Configuration â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    st.subheader("ðŸ“ Route Configuration")
    available_cities = ["Chennai", "Vellore", "Salem", "Bangalore", "Krishnagiri"]
    
    source_city = st.selectbox(
        "Source City",
        options=available_cities,
        index=0  # Default to Chennai
    )
    
    destination_city = st.selectbox(
        "Destination City",
        options=available_cities,
        index=3  # Default to Bangalore
    )
    
    if source_city == destination_city:
        st.warning("âš ï¸ Source and destination cannot be the same!")

    st.divider()

    distance = st.slider(
        "Distance (km)", min_value=50, max_value=500, value=300, step=10
    )

    traffic_map = {0: "ðŸŸ¢ Low", 1: "ðŸŸ¡ Medium", 2: "ðŸ”´ High"}
    traffic_label = st.selectbox(
        "Traffic Level",
        options=list(traffic_map.values()),
    )
    traffic = [k for k, v in traffic_map.items() if v == traffic_label][0]

    weather_map = {0: "â˜€ï¸ Clear", 1: "ðŸŒ§ Rain", 2: "â›ˆ Storm"}
    weather_label = st.selectbox(
        "Weather Condition",
        options=list(weather_map.values()),
    )
    weather = [k for k, v in weather_map.items() if v == weather_label][0]

    predict_btn = st.button("ðŸ” Predict", width='stretch', type="primary")
    st.divider()
    st.caption(f"Route: {source_city} â†’ {destination_city}")

# â”€â”€ Initialize session state â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if "prediction_result" not in st.session_state:
    st.session_state.prediction_result = None
if "prediction_payload" not in st.session_state:
    st.session_state.prediction_payload = None

# â”€â”€ Main area â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if predict_btn:
    # Validate that source and destination are different
    if source_city == destination_city:
        st.error("âŒ Source and destination cities must be different!")
    else:
        payload = {
            "shipment_id": shipment_id,
            "distance":    distance,
            "traffic":     traffic,
            "weather":     weather,
            "source":      source_city,
            "destination": destination_city,
        }

        # Use deployed backend for inference.
        result = None
        try:
            with st.spinner("⏳ Connecting to AI engine..."):
                resp = requests.post(
                    API_URL,
                    json=payload,
                    timeout=60,
                )
            resp.raise_for_status()
            result = resp.json()
        except Exception as e:
            st.warning(
                "⚠️ Backend is waking up (Render cold start). "
                "Please wait 30-60 seconds and try again."
            )
            st.stop()

        # Store result and payload in session state so they persist across re-runs
        if result:
            st.session_state.prediction_result = result
            st.session_state.prediction_payload = payload

# â”€â”€ Display results (persisted in session state) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
if st.session_state.prediction_result:
    result = st.session_state.prediction_result
    # Alert banner
    if result.get("alert"):
        st.error(f"ðŸš¨ {result['alert_msg']}")
    else:
        st.success("âœ… Shipment looks good â€“ low risk of delay.")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Shipment ID",  result["shipment_id"])
    with col2:
        st.metric("Delay Risk",   result["risk_pct"])
    with col3:
        st.metric("Status",       result["status"])
    with col4:
        st.metric("Distance",     f"{distance} km")

    st.divider()

    # Route info header
    if st.session_state.prediction_payload:
        source = st.session_state.prediction_payload.get("source", "Unknown")
        destination = st.session_state.prediction_payload.get("destination", "Unknown")
        st.markdown(f"### ðŸ“ Route: **{source}** â†’ **{destination}**")

    # Route display
    col_route, col_all = st.columns([2, 3])

    with col_route:
        st.subheader("ðŸ—ºï¸ Best Route")
        route_str = " â†’ ".join(result["route"])
        st.markdown(
            f'<div class="route-box">{route_str}</div>',
            unsafe_allow_html=True,
        )
        
        # Show cost details for best route
        if result.get("all_routes") and len(result["all_routes"]) > 0:
            best = result["all_routes"][0]
            st.metric("Base Distance", f"{best.get('base_distance', 'N/A')} km")
            st.metric("Adjusted Cost", f"{best.get('risk_adjusted_cost', 'N/A')} km-units")
        
        st.caption("âœ… Dijkstra shortest path (risk-adjusted)")

    with col_all:
        st.subheader("ðŸ“‹ All Available Routes")
        rows = []
        for i, r in enumerate(result.get("all_routes", []), 1):
            rows.append({
                "Rank":  i,
                "Route": " â†’ ".join(r["route"]),
                "Base Distance (km)": r.get("base_distance", r.get("cost", "-")),
                "Adjusted Cost": r.get("risk_adjusted_cost", r.get("cost", "-")),
            })
        if rows:
            df_routes = pd.DataFrame(rows)
            st.dataframe(df_routes, width='stretch', hide_index=True)
            
            # Show cost comparison explanation
            with st.expander("ðŸ’¡ How costs are calculated"):
                st.markdown("""
                **Base Distance**: Actual road distance in km (no adjustments)
                
                **Adjusted Cost**: Distance multiplied by risk factors:
                - Traffic multiplier: Low=1.0x | Medium=1.2x | High=1.5x
                - Weather multiplier: Clear=1.0x | Rain=1.3x | Storm=1.6x
                - **Adjusted Cost = Base Distance Ã— Traffic Factor Ã— Weather Factor**
                
                âœ… **Why the best route is recommended**: It balances distance and risk conditions
                """)

    st.divider()

    # Risk gauge (simple visual)
    st.subheader("ðŸ“Š Delay Risk Gauge")
    risk_val = result["risk"]
    bar_color = "red" if risk_val > 0.7 else ("orange" if risk_val > 0.4 else "green")
    st.progress(risk_val)
    risk_col = "risk-high" if risk_val > 0.7 else "risk-low"
    st.markdown(
        f'<p class="big-metric {risk_col}">{risk_val * 100:.1f}% Delay Probability</p>',
        unsafe_allow_html=True,
    )

    st.divider()

    # â”€â”€ AI Explanation + Route Visualization (Side by Side) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    col_ai, col_map = st.columns([1.2, 1.3])

    # â”€â”€ LEFT COLUMN: AI Explanation â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with col_ai:
        st.subheader("ðŸ¤– AI Logistics Assistant")
        
        # Generate detailed explanation with current parameters
        if st.session_state.prediction_payload:
            payload_stored = st.session_state.prediction_payload
            detailed_explanation = generate_detailed_explanation(
                result,
                payload_stored["distance"],
                payload_stored["traffic"],
                payload_stored["weather"]
            )
            st.markdown(
                f'<div class="explanation-box">{detailed_explanation}</div>',
                unsafe_allow_html=True,
            )
        elif result.get("explanation"):
            st.markdown(
                f'<div class="explanation-box">{result["explanation"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.info("AI explanation generation in progress or unavailable.")

    # â”€â”€ RIGHT COLUMN: Route Visualization â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
    with col_map:
        st.subheader("ðŸ—ºï¸ Route Visualization")
        
        map_choice = st.radio(
            "Map Type:",
            options=["Interactive Folium Map", "Google Maps (if API available)"],
            horizontal=True,
            label_visibility="collapsed"
        )

        if map_choice == "Interactive Folium Map":
            show_map_folium(result["route"])
        else:
            # Try to use Google Maps API key from environment
            google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY")
            if google_maps_key:
                show_map_google(result["route"], api_key=google_maps_key)
            else:
                st.info("Google Maps API key not configured. Showing Folium map instead.")
                show_map_folium(result["route"])

    st.divider()

    # Input summary
    with st.expander("ðŸ”Ž Input Summary"):
        if st.session_state.prediction_payload:
            st.json(st.session_state.prediction_payload)
        else:
            st.info("No input data available")

    # Firebase doc info
    if result.get("firebase_doc") not in (None, "offline-mode", "demo-mode"):
        st.caption(f"âœ… Saved to Firebase: doc_id = {result['firebase_doc']}")
    else:
        st.caption("â„¹ï¸ Firebase: demo/offline mode â€“ result not persisted.")

    # Add button to clear results
    if st.button("ðŸ—‘ï¸ Clear Results"):
        st.session_state.prediction_result = None
        st.rerun()

else:
    # Landing state
    st.info("ðŸ‘ˆ Configure shipment details in the sidebar, then click **Predict**.")

    st.subheader("How PASCI Works")
    col_a, col_b, col_c = st.columns(3)
    with col_a:
        st.markdown("### ðŸ¤– ML Prediction\nRandom Forest model trained on 1 000 synthetic shipments predicts delay probability.")
    with col_b:
        st.markdown("### ðŸ—ºï¸ Route Optimisation\nDijkstra's algorithm selects the least-cost path with dynamic traffic & weather penalties.")
    with col_c:
        st.markdown("### ðŸ”¥ Firebase Storage\nEvery prediction is stored in Firestore for historical analytics and audit.")

# â”€â”€ History tab (sidebar trigger) â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€
with st.sidebar:
    st.subheader("ðŸ“œ Shipment History")
    if st.button("Load History from Firebase", width='stretch'):
        try:
            resp = requests.get(f"{API_BASE_URL}/history?limit=5", timeout=60)
            if resp.status_code == 200:
                data = resp.json()
                if data["count"] == 0:
                    st.info("No records yet.")
                else:
                    for rec in data["shipments"]:
                        st.markdown(
                            f"**{rec.get('shipment_id','N/A')}** â€“ "
                            f"Risk: {rec.get('risk', 0)*100:.0f}% | "
                            f"Route: {' â†’ '.join(rec.get('route', []))}"
                        )
            else:
                st.warning("History unavailable.")
        except Exception:
            st.warning("API offline â€“ history unavailable.")
