# core/lp_solver.py
import pulp as p
import numpy as np
from typing import List, Tuple

def solve_p_median(f: List[float], c: List[List[float]], p_val: int) -> Tuple[List[bool], float, str]:
    n_c = len(c)
    n_f = len(f)

    model = p.LpProblem('P-Median', p.LpMinimize)

    # Decision variables
    y = [p.LpVariable(f'y{j}', cat=p.LpBinary) for j in range(n_f)]
    x = [[p.LpVariable(f'x{i}_{j}', cat=p.LpBinary) for j in range(n_f)] for i in range(n_c)]

    # Objective function
    model += p.lpSum(f[j] * y[j] for j in range(n_f)) + \
             p.lpSum(c[i][j] * x[i][j] for i in range(n_c) for j in range(n_f))

    # Constraints
    for i in range(n_c):
        model += p.lpSum(x[i][j] for j in range(n_f)) == 1

    for i in range(n_c):
        for j in range(n_f):
            model += x[i][j] <= y[j]

    model += p.lpSum(y[j] for j in range(n_f)) == p_val

    status_code = model.solve()
    status = p.LpStatus[status_code]

    if status != 'Optimal':
        return [], float('inf'), status

    
    result = [p.value(y[j]) > 0.5 for j in range(n_f)]
    cost = evaluate_solution_cost(f, c, result)

    return result, cost, status


def evaluate_solution_cost(f: List[float], c: List[List[float]], selected: List[bool]) -> float:
    total = sum(f[j] for j, active in enumerate(selected) if active)

    for i in range(len(c)):
        min_cost = float('inf')
        for j in range(len(f)):
            if selected[j]:
                min_cost = min(min_cost, c[i][j])
        total += min_cost

    return total
