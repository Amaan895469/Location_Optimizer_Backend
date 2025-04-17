# src/core/ga_solver.py

import random
import operator
import numpy as np
import pandas as pd
import time
from typing import List, Tuple, Dict
from math import sin, cos, sqrt, atan2, radians

class City:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance(self, city) -> float:
        R = 6373.0  # Earth radius in km
        lat1 = radians(self.x)
        lon1 = radians(self.y)
        lat2 = radians(city.x)
        lon2 = radians(city.y)

        dlat = lat2 - lat1
        dlon = lon2 - lon1

        a = sin(dlat/2)**2 + cos(lat1)*cos(lat2)*sin(dlon/2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        return R * c
    
    def __eq__(self, other):
        if not isinstance(other, City):
            return False
        return self.x == other.x and self.y == other.y
    
    def __repr__(self):
        return f"({self.x},{self.y})"

class Fitness:
    def __init__(self, route):
        self.route = route
        self.distance = 0
        self.fitness = 0.0

    def routeDistance(self):
        if self.distance == 0:
            pathDistance = 0
            for i in range(len(self.route)):
                fromCity = self.route[i]
                toCity = self.route[(i + 1) % len(self.route)]
                pathDistance += fromCity.distance(toCity)
            self.distance = pathDistance
        return self.distance

    def routeFitness(self):
        if self.fitness == 0:
            self.fitness = 1 / float(self.routeDistance())
        return self.fitness

def solve_ga_route(
    coordinates: List[Tuple[float, float]],
    pop_size: int = 200,
    elite_size: int = 10,
    mutation_rate: float = 0.002,
    generations: int = 1000,log_callback=None 
) -> Dict:
    start_time = time.time()
    cityList = [City(lat, lon) for lat, lon in coordinates]
    
    # Save the original coordinates for indexing later
    original_coords = [(city.x, city.y) for city in cityList]

    def createRoute(cityList):
        return random.sample(cityList, len(cityList))

    def initialPopulation(popSize, cityList):
        return [createRoute(cityList) for _ in range(popSize)]

    def rankRoutes(population):
        fitnessResults = {}
        for i in range(len(population)):
            fitnessResults[i] = Fitness(population[i]).routeFitness()
        return sorted(fitnessResults.items(), key=operator.itemgetter(1), reverse=True)

    def FP_selection(popRanked, eliteSize):
        selectionResults = []
        df = pd.DataFrame(np.array(popRanked), columns=["Index", "Fitness"])
        df['cum_sum'] = df.Fitness.cumsum()
        df['cum_perc'] = 100 * df.cum_sum / df.Fitness.sum()

        for i in range(eliteSize):
            selectionResults.append(popRanked[i][0])
            
        for _ in range(len(popRanked) - eliteSize):
            pick = 100 * random.random()
            for i in range(len(popRanked)):
                if pick <= df.iat[i, 3]:
                    selectionResults.append(popRanked[i][0])
                    break
        return selectionResults

    def matingPool(population, selectionResults):
        return [population[int(i)] for i in selectionResults]

    def OX(parent1, parent2):
        child = []
        childA = []
        
        geneA, geneB = random.sample(range(len(parent1)), 2)
        startGene = min(geneA, geneB)
        endGene = max(geneA, geneB)
        
        for i in range(startGene, endGene):
            childA.append(parent1[i])
        
        p2_rolled = list(np.roll(parent2, -endGene))
        selP2 = [item for item in p2_rolled if item not in childA]
        
        child = childA + selP2
        return child, startGene, endGene

    def CX(parent1, parent2):
        child = [None] * len(parent1)
        start = random.randint(0, len(parent1) - 1)
        current = start
        
        # Fill in the cycle
        while True:
            child[current] = parent1[current]
            current = parent1.index(parent2[current])
            if current == start:
                break
                
        # Fill remaining positions from parent2
        for i in range(len(child)):
            if child[i] is None:
                child[i] = parent2[i]
                
        return child, start

    def INV(parent):
        child = parent.copy()
        geneA, geneB = random.sample(range(len(parent)), 2)
        startGene = min(geneA, geneB)
        endGene = max(geneA, geneB)
        
        child[startGene:endGene+1] = reversed(child[startGene:endGene+1])
        return child, startGene, endGene

    def crossoverPopulation(matingpool, eliteSize):
        children = []
        length = len(matingpool) - eliteSize
        pool = random.sample(matingpool, len(matingpool))

        # Keep elite
        for i in range(eliteSize):
            children.append(matingpool[i])
        
        # Crossover for the rest
        for i in range(length):
            r = random.random()
            if r > 0.7:
                child, _, _ = OX(pool[i], pool[len(matingpool)-i-1])
            elif r > 0.3:
                child, _ = CX(pool[i], pool[len(matingpool)-i-1])
            else:
                child, _, _ = INV(pool[i])
            children.append(child)
            
        return children

    def mutate(individual, mutationRate):
        for i in range(len(individual)):
            if random.random() < mutationRate:
                j = random.randint(0, len(individual) - 1)
                individual[i], individual[j] = individual[j], individual[i]
        return individual

    def mutatePopulation(population, mutationRate):
        return [mutate(ind.copy(), mutationRate) for ind in population]

    def nextGeneration(currentGen, eliteSize, mutationRate):
        popRanked = rankRoutes(currentGen)
        selectionResults = FP_selection(popRanked, eliteSize)
        matingpool = matingPool(currentGen, selectionResults)
        children = crossoverPopulation(matingpool, eliteSize)
        nextGen = mutatePopulation(children, mutationRate)
        return nextGen

    # Create initial population
    pop = initialPopulation(pop_size, cityList)
    for i in range(generations):
        pop = nextGeneration(pop, elite_size, mutation_rate)
        if log_callback:
            best_dist = 1 / rankRoutes(pop)[0][1]
            log_callback(i + 1, best_dist)
    
   # Get best route
    best_idx = rankRoutes(pop)[0][0]
    best_route = pop[best_idx]
    best_distance = Fitness(best_route).routeDistance()
    
    # Helper to match coordinates with tolerance
    def find_index(coord_list, target, tol=1e-6):
        for idx, coord in enumerate(coord_list):
            if abs(coord[0] - target[0]) < tol and abs(coord[1] - target[1]) < tol:
                return idx
        raise ValueError(f"{target} is not in list")

    # Convert city objects to original indices
    route_indices = []
    for city in best_route:
        city_tuple = (city.x, city.y)
        route_indices.append(find_index(coordinates, city_tuple) + 1)  
    
    end_time = time.time()
    
    return {
        "route_indices": route_indices,
        "total_distance": round(best_distance, 4),
        "computation_time": round(end_time - start_time, 2),
        "status": "success"
    }