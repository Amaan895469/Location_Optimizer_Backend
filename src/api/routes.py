# src/api/routes.py

from flask import Flask, request, jsonify
import pandas as pd
from io import TextIOWrapper
import json
from src.core.lp_solver import solve_p_median

app = Flask(__name__)

@app.route("/solve/p-median", methods=["POST"])
def solve_pmedian_csv():
    # Check for uploaded matrix
    if 'matrix_file' not in request.files:
        return jsonify({"error": "matrix.csv not uploaded"}), 400

    try:
        # Read CSV file (distance matrix)
        matrix_file = request.files['matrix_file']
        matrix_df = pd.read_csv(TextIOWrapper(matrix_file, encoding='utf-8'), header=None)
        distance_matrix = matrix_df.to_numpy().tolist()

        # Parse fixed costs (as JSON string)
        fixed_costs_raw = request.form.get("fixed_costs")
        fixed_costs = json.loads(fixed_costs_raw) if fixed_costs_raw else []

        # Parse p_val
        p_val = int(request.form.get("p_val", 2))

        if not fixed_costs:
            return jsonify({"error": "Missing fixed_costs"}), 400

        # Solve
        selected, cost, status = solve_p_median(fixed_costs, distance_matrix, p_val)

        return jsonify({
            "selected_facilities": selected,
            "total_cost": cost,
            "status": status
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500
