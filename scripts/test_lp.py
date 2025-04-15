# scripts/test_lp.py or API call

import pandas as pd
from src.core.lp_solver import solve_p_median

# Load your data
fixed_costs = [600.00, 528.17, 730.43, 606.06, 1200.00, 4166.67, 833.33, 666.67,
               1200.00, 1111.11, 625.00, 1200.00, 833.33, 1450.00, 568.18,
               1041.67, 1653.85, 1285.71, 1000.00, 750.00, 965.52, 550.00, 923.08]

matrix = pd.read_csv('data/matrix.csv', header=None).to_numpy().tolist()

p_value = 2
selected_facilities, total_cost, status = solve_p_median(fixed_costs, matrix, p_value)

print("Selected Facilities:", selected_facilities)
print("Total Cost:", total_cost)
print("Solver Status:", status)
