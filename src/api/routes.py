# src/api/routes.py

from flask import Flask, request, jsonify
import pandas as pd
from io import TextIOWrapper
import json
from src.core.lp_solver import solve_p_median
from src.core.ga_solver import solve_ga_route
from uuid import uuid4
from threading import Thread
from flask_cors import CORS
from dotenv import load_dotenv
from math import radians, cos, sin, sqrt, atan2

load_dotenv()

allowed_origins = os.environ.get('ALLOWED_ORIGINS', '')
origins = allowed_origins.split(',') if allowed_origins else []

CORS(app, origins=origins)
def haversine(lat1, lon1, lat2, lon2):
    R = 6371  # km
    dlat, dlon = radians(lat2 - lat1), radians(lon2 - lon1)
    a = sin(dlat/2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon/2)**2
    return 2 * R * atan2(sqrt(a), sqrt(1 - a))

    
@app.route("/solve/p-median-coords", methods=["POST"])
def solve_pmedian_coords():
    try:
        data = request.get_json()
        coords = data.get("coordinates", [])
        fixed_costs = data.get("fixed_costs", [])
        p_val = int(data.get("p_val", 2))

        if not coords or not fixed_costs:
            return jsonify({"error": "Missing coordinates or fixed costs"}), 400

        # Generate distance matrix: c[i][j] = dist(client_i, facility_j)
        n = len(coords)
        c = [[haversine(*coords[i], *coords[j]) for j in range(n)] for i in range(n)]

        selected, cost, status = solve_p_median(fixed_costs, c, p_val)

        return jsonify({
            "selected_facilities": selected,
            "total_cost": cost,
            "status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


job_results = {}

@app.route('/solve/ga', methods=['POST'])
def solve_ga_api():
    data = request.get_json()
    coords = data.get("coordinates")
    generations = data.get("generations", 1000)
    pop_size = data.get("pop_size", 200)
    elite_size = data.get("elite_size", 10)
    mutation_rate = data.get("mutation_rate", 0.002)

    if not coords:
        return jsonify({"error": "Missing coordinates"}), 400

    job_id = str(uuid4())
    job_results[job_id] = {"status": "processing"}

    def run_ga_job():
        try:
            log = []
            def log_callback(gen, best_dist):
                log.append({"generation": gen, "best_distance": best_dist})

            result = solve_ga_route(
                coordinates=coords,
                generations=generations,
                pop_size=pop_size,
                elite_size=elite_size,
                mutation_rate=mutation_rate,
                log_callback=log_callback
            )
            
            # Add the actual route coordinates for the polyline
            if "route_indices" in result:
                ordered_route = [coords[idx-1] for idx in result["route_indices"]]
                # Add the first point again to close the loop
                if ordered_route:
                    ordered_route.append(ordered_route[0])
                result["route"] = ordered_route
                
            result["log"] = log
            job_results[job_id] = {"status": "completed", "result": result}
        except Exception as e:
            job_results[job_id] = {"status": "failed", "error": str(e)}

    Thread(target=run_ga_job).start()

    return jsonify({"job_id": job_id}), 202  # Accepted


@app.route('/check-status/<job_id>', methods=['GET'])
def check_status(job_id):
    job = job_results.get(job_id)
    if not job:
        return jsonify({"error": "Invalid job ID"}), 404

    return jsonify(job)