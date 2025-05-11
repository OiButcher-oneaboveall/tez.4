
import random
import numpy as np
from data_config import (
    cities, distance_matrix, hourly_speed_matrix,
    hourly_risk_matrix, fuel_consumption_matrix,
    co2_emission_factor, time_windows, service_times, START_HOUR
)

def get_speed(i, j, hour):
    idx = hour - START_HOUR
    return hourly_speed_matrix[i][j][idx] if 0 <= idx < 12 else 90

def get_risk(i, j, hour):
    idx = hour - START_HOUR
    return hourly_risk_matrix[i][j][idx] if 0 <= idx < 12 else 0.5

def get_fuel(i, j, hour):
    idx = hour - START_HOUR
    return fuel_consumption_matrix[i][j][idx] if 0 <= idx < 12 else 0.35

def compute_leg(i, j, hour, minute):
    distance = distance_matrix[i][j]
    speed = get_speed(i, j, hour)
    travel_min = (distance / speed) * 60
    fuel = distance * get_fuel(i, j, hour)
    risk = get_risk(i, j, hour)
    co2 = fuel * co2_emission_factor
    return travel_min, fuel, co2, risk

def route_metrics(route):
    time, fuel, co2, risk = 0, 0, 0, 0
    hour, minute = START_HOUR, 0
    log = []

    for i in range(len(route) - 1):
        a, b = route[i], route[i+1]
        leg_min, leg_fuel, leg_co2, leg_risk = compute_leg(a, b, hour, minute)
        time += leg_min
        fuel += leg_fuel
        co2 += leg_co2
        risk += leg_risk

        minute += int(leg_min)
        hour += minute // 60
        minute %= 60

        if b != 0:
            early, late = time_windows[b]
            arr_min = hour * 60 + minute
            if arr_min < early * 60:
                wait = early * 60 - arr_min
                time += wait
                minute += wait
                hour += minute // 60
                minute %= 60
            elif arr_min > late * 60:
                return float('inf'), float('inf'), float('inf'), float('inf'), []

            service = service_times.get(b, 0)
            time += service
            minute += service
            hour += minute // 60
            minute %= 60

        log.append({
            "from": cities[a], "to": cities[b],
            "travel_min": round(leg_min, 1),
            "fuel": round(leg_fuel, 2),
            "co2": round(leg_co2, 2),
            "risk": round(leg_risk, 2)
        })

    return time, fuel, co2, risk, log

def fitness(route, hedef="denge", max_risk=1.2):
    t, f, c, r, _ = route_metrics(route)
    if r > max_risk:
        return float('inf')
    if any(x == float('inf') for x in [t, f, c, r]):
        return float('inf')
    if hedef == "süre":
        return t
    elif hedef == "emisyon":
        return c
    elif hedef == "risk":
        return r
    elif hedef == "tümü":
        return 0.4 * t + 0.3 * c + 0.3 * r
    return 0.5 * t + 0.5 * c

def selection(pop, hedef, max_risk=1.2):
    return min(random.sample(pop, 5), key=lambda x: fitness(x, hedef, max_risk))

def crossover(p1, p2):
    start, end = sorted(random.sample(range(1, len(p1)-1), 2))
    child = [None] * len(p1)
    child[start:end] = p1[start:end]
    pointer = 1
    for gene in p2[1:-1]:
        if gene not in child:
            while child[pointer] is not None:
                pointer += 1
            child[pointer] = gene
    child[0] = child[-1] = 0
    return child

def mutate(route, rate=0.02):
    for i in range(1, len(route)-2):
        if random.random() < rate:
            j = random.randint(1, len(route)-2)
            route[i], route[j] = route[j], route[i]

def initialize_population(size, n):
    pop = []
    for _ in range(size):
        genes = list(range(1, n))
        random.shuffle(genes)
        pop.append([0] + genes + [0])
    return pop

def get_best_route(pop_size=200, generations=500, hedef="denge", max_risk=1.2):
    pop = initialize_population(pop_size, len(cities))
    for _ in range(generations):
        new_pop = []
        for _ in range(pop_size):
            p1, p2 = selection(pop, hedef, max_risk), selection(pop, hedef, max_risk)
            child = crossover(p1, p2)
            mutate(child)
            new_pop.append(child)
        pop = new_pop
    valid = [r for r in pop if fitness(r, hedef, max_risk) != float('inf')]
    if valid:
        best = min(valid, key=lambda x: fitness(x, hedef))
        t, f, c, r, log = route_metrics(best)
        return best, t, f, c, r, log
    return None
