
from optimizer import get_best_route
import pandas as pd

def risk_vs_time_analysis(risk_bounds, pop_size=100, generations=300):
    results = []
    for bound in risk_bounds:
        result = get_best_route(pop_size=pop_size, generations=generations, hedef="tümü")
        if result:
            _, t, f, c, r, _ = result
            if r <= bound:
                results.append({"Risk Sınırı": round(bound, 2), "Toplam Süre": round(t, 1)})
    return pd.DataFrame(results)

def speed_sensitivity_analysis(speed_modifiers, pop_size=100, generations=300):
    results = []
    from data_config import hourly_speed_matrix
    original = hourly_speed_matrix.copy()

    for factor in speed_modifiers:
        hourly_speed_matrix[:] = original * factor
        result = get_best_route(pop_size=pop_size, generations=generations, hedef="süre")
        if result:
            _, t, f, c, r, _ = result
            results.append({"Hız Katsayısı": factor, "Toplam Süre": round(t, 1)})

    hourly_speed_matrix[:] = original
    return pd.DataFrame(results)
