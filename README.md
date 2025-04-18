# 🧠 Location Optimizer Backend (Flask API)

This is the **Flask backend** for the **Location Optimization Tool**, a geospatial decision support system. It provides RESTful APIs to solve:
- The **P-Median problem** for facility location optimization  
- The **Traveling Salesman Problem (TSP)** using a **Genetic Algorithm (GA)**

> The backend is designed to work with the React frontend deployed [here](https://or-frontend-amber.vercel.app) and supports both synchronous and asynchronous operations.

---

## ⚙️ Tech Stack
- **Flask** for API framework  
- **PuLP** for solving the P-Median Linear Program  
- **NumPy**, **Pandas** for computation  
- **Gunicorn** for production serving  
- **Flask-CORS** for cross-origin communication  
- **dotenv** for environment configuration

---

## 🚀 Deployment (Render)
- Backend URL: [https://operations-research-project.onrender.com](https://operations-research-project.onrender.com)

---

## 📡 API Endpoints

### 🏭 `POST /solve/p-median-coords`
Solves the **P-Median problem** for selecting `p` facility locations given:
- A list of coordinates  
- Fixed facility costs  
- Value of `p`

#### 📥 Request Body:
```json
{
  "coordinates": [[lat1, lon1], [lat2, lon2], ...],
  "fixed_costs": [100, 200, 150, ...],
  "p_val": 3
}
```

#### 📤 Response:
```json
{
  "selected_facilities": [false, true, false, true],
  "total_cost": 374.52,
  "status": "Optimal"
}
```

#### 🧠 Logic:
- Computes all pairwise distances using the Haversine formula
- Solves a Mixed-Integer Linear Program using PuLP

#### ⚠️ Limitations:
- Assumes all points can be both clients and candidate facilities
- Returns `[]` and `Infinity` if LP is infeasible or not optimal

### 🧬 `POST /solve/ga`
Starts an **asynchronous Genetic Algorithm** to solve a TSP over the provided coordinates.

#### 📥 Request Body:
```json
{
  "coordinates": [[lat1, lon1], [lat2, lon2], ...],
  "generations": 1000,
  "pop_size": 200,
  "elite_size": 10,
  "mutation_rate": 0.01
}
```

#### 📤 Response (immediate):
```json
{
  "job_id": "abcd-1234"
}
```

### ⏳ `GET /check-status/<job_id>`

#### 📤 Response:
```json
{
  "status": "completed",
  "result": {
    "route_indices": [1, 4, 3, 2, 1],
    "route": [[...], [...], ...],
    "total_distance": 123.45,
    "computation_time": 2.34,
    "status": "success",
    "log": [
      {"generation": 1, "best_distance": 700.3},
      ...
    ]
  }
}
```

#### 🧠 GA Logic:
- Uses real-world distance via the Haversine formula
- Implements selection, crossover (OX/CX), and mutation (swap/inversion)
- Logs progress over generations

#### ⚠️ Limitations:
- No persistent storage: results vanish after app restarts
- Route indices assume original coordinate order
- Stochastic: may produce different solutions across runs

---

## 🧪 Local Setup

### 1. Clone & Install
```bash
git clone https://github.com/your-username/location-optimizer-backend.git
cd location-optimizer-backend
pip install -r requirements.txt
```

### 2. Configure Environment
Create a `.env` file:
```env
FLASK_ENV=development
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 3. Run Locally
```bash
python -m src.api.routes
```

Or for production:
```bash
gunicorn src.api.routes:app
```

---

## 🧾 File Structure
```
├── src/
│   ├── api/
│   │   └── routes.py        # Main Flask routes & job manager
│   └── core/
│       ├── lp_solver.py     # P-Median optimizer using PuLP
│       └── ga_solver.py     # TSP optimizer using Genetic Algorithm
├── requirements.txt
└── .env
```

---

## 📌 Requirements
```
flask>=2.0.0
flask-cors>=3.0.10
pulp>=2.0.0
numpy>=1.19.0
pandas>=1.0.0
gunicorn==21.2.0
python-dotenv
```
