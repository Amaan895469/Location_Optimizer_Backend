# scripts/test_ga.py

from src.core.ga_solver import solve_ga_route

# Coordinates (Lat, Lng) from your original project (Genoa region, Italy)
coordinates = [
    (44.40711, 8.96546), (44.41308, 8.96966), (44.40856, 8.95999), (44.40726, 8.97667),
    (44.3991, 8.96421), (44.4064, 8.952), (44.42032, 8.96635), (44.41182, 8.95258),
    (44.40252, 8.95401), (44.41748, 8.95572), (44.39676, 8.97581), (44.40275, 8.98595),
    (44.42269, 8.95693), (44.41892, 8.94967), (44.41365, 8.94446), (44.40682, 8.93501),
    (44.40486, 8.9435), (44.39637, 8.94834), (44.39343, 8.985893), (44.40234, 8.93884),
    (44.41027, 8.93558), (44.41389, 8.93239), (44.40796, 8.92816)
]

# Run the GA solver
result = solve_ga_route(
    coordinates=coordinates,
    pop_size=200,
    elite_size=10,
    mutation_rate=0.002,
    generations=3000
)

# Output results
print("✅ Genetic Algorithm Route Optimization")
print("Route indices (visit order):", result["route_indices"])
print("Total distance (km):", result["total_distance"])
print("Solver status:", result["status"])
