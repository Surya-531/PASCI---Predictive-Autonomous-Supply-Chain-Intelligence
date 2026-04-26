"""
PASCI – Route Optimization Module
Uses Dijkstra's algorithm (via NetworkX) to find the lowest-cost path
between any two cities, with dynamic risk-aware weight adjustments for
traffic and weather conditions.
"""

import networkx as nx
from typing import List, Dict


# ── Base road network with ALL direct routes (distances in km) ────────────────
# Complete connectivity between all major South Indian logistics hubs
BASE_GRAPH = {
    # Chennai connections
    ("Chennai", "Vellore"):       140,
    ("Chennai", "Salem"):         340,
    ("Chennai", "Krishnagiri"):   300,
    ("Chennai", "Bangalore"):     350,
    
    # Vellore connections
    ("Vellore", "Bangalore"):     210,
    ("Vellore", "Krishnagiri"):   120,  # ✅ ADDED: Direct route (was missing!)
    ("Vellore", "Salem"):         180,  # ✅ ADDED: Direct route
    
    # Bangalore connections
    ("Bangalore", "Krishnagiri"):  90,
    ("Bangalore", "Salem"):        200,
    
    # Krishnagiri connections
    ("Krishnagiri", "Salem"):     140,
}

# ── Risk factor multipliers (not additive penalties) ─────────────────────────
# traffic:  0=low, 1=medium, 2=high
# weather:  0=clear, 1=rain, 2=storm
TRAFFIC_FACTOR = {0: 1.0, 1: 1.2, 2: 1.5}      # 0%, 20%, 50% increase
WEATHER_FACTOR = {0: 1.0, 1: 1.3, 2: 1.6}      # 0%, 30%, 60% increase


def build_graph(traffic: int, weather: int) -> nx.Graph:
    """
    Construct a weighted undirected graph with risk-aware cost function.
    
    Instead of adding constant penalties, we use a multiplicative risk factor:
    adjusted_weight = base_distance * traffic_factor * weather_factor
    
    This ensures shorter direct routes are favored over longer indirect ones.
    """
    traffic_mult = TRAFFIC_FACTOR.get(traffic, 1.0)
    weather_mult = WEATHER_FACTOR.get(weather, 1.0)
    risk_factor = traffic_mult * weather_mult

    G = nx.Graph()
    for (u, v), base_distance in BASE_GRAPH.items():
        adjusted_weight = base_distance * risk_factor
        G.add_edge(u, v, weight=adjusted_weight, base_distance=base_distance, risk_factor=risk_factor)
    
    return G


def get_route_cost(G: nx.Graph, path: List[str]) -> float:
    """
    Calculate total cost of a route given the graph.
    
    Args:
        G: NetworkX graph
        path: List of city names
    
    Returns:
        Total cost (sum of all edge weights)
    """
    cost = sum(
        G[path[i]][path[i + 1]]["weight"] for i in range(len(path) - 1)
    )
    return cost


def get_best_route(
    traffic: int,
    weather: int,
    source: str = "Chennai",
    destination: str = "Bangalore",
) -> List[str]:
    """
    Return the optimal (lowest-cost) path from source to destination using Dijkstra's.

    Args:
        traffic     : 0=low | 1=medium | 2=high
        weather     : 0=clear | 1=rain | 2=storm
        source      : start city (default Chennai)
        destination : end city   (default Bangalore)

    Returns:
        List of city names representing the best route.
    """
    G = build_graph(traffic, weather)
    
    try:
        path = nx.shortest_path(G, source=source, target=destination, weight="weight")
        cost = get_route_cost(G, path)
        
        traffic_name = ["Low", "Medium", "High"][traffic]
        weather_name = ["Clear", "Rain", "Storm"][weather]
        
        print(f"\n[route_optimizer] Best Route: {' → '.join(path)}")
        print(f"[route_optimizer] Cost: {cost:.2f} km-units (Traffic: {traffic_name}, Weather: {weather_name})")
        
        return path
    except nx.NetworkXNoPath:
        print(f"[route_optimizer] No path found from {source} to {destination}")
        return [source, destination]


def get_all_routes(
    traffic: int,
    weather: int,
    source: str = "Chennai",
    destination: str = "Bangalore",
) -> List[Dict]:
    """
    Return all simple paths ranked by cost with detailed cost breakdowns.
    
    Returns:
        List of dicts with 'route', 'cost', 'breakdown' keys
    """
    G = build_graph(traffic, weather)
    
    try:
        paths = list(nx.all_simple_paths(G, source=source, target=destination))
    except nx.NetworkXNoPath:
        return []
    
    ranked = []
    for p in paths:
        cost = get_route_cost(G, p)
        
        # Calculate cost breakdown (base + risk adjustment)
        base_cost = sum(G[p[i]][p[i + 1]]["base_distance"] for i in range(len(p) - 1))
        risk_factor = G[p[0]][p[1]]["risk_factor"]
        
        ranked.append({
            "route": p,
            "cost": round(cost, 2),
            "base_distance": round(base_cost, 2),
            "risk_adjusted_cost": round(cost, 2),
        })
    
    ranked.sort(key=lambda x: x["cost"])
    
    # 🔥 DEBUG: Print all routes with costs
    print(f"\n[route_optimizer] All routes from {source} to {destination}:")
    for i, r in enumerate(ranked, 1):
        print(f"  {i}. {' → '.join(r['route'])} | Base: {r['base_distance']} km | Adjusted: {r['cost']} km-units")
    
    return ranked


if __name__ == "__main__":
    # Quick smoke-test
    for t, w in [(0, 0), (2, 0), (0, 2), (2, 2)]:
        print(f"\ntraffic={t}, weather={w}")
        print("  Best :", get_best_route(t, w))
        print("  All  :", get_all_routes(t, w))
