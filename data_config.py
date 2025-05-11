
import numpy as np

# Şehir isimleri
cities = ["Rafineri", "Gürpınar", "Yenikapı", "Selimiye", "İçerenköy", "Tophane", "Alibeyköy", "İstinye"]

# Şehir koordinatları (İstanbul'a göre)
city_coords = {
    "Rafineri": (40.967, 29.126),
    "Gürpınar": (40.976, 28.616),
    "Yenikapı": (41.003, 28.949),
    "Selimiye": (41.003, 29.019),
    "İçerenköy": (40.979, 29.106),
    "Tophane": (41.027, 28.978),
    "Alibeyköy": (41.077, 28.943),
    "İstinye": (41.109, 29.060)
}

# Mesafe matrisi (km)
distance_matrix = np.array([
    [0, 66.8, 105, 123, 130, 106, 109, 113],
    [66.8, 0, 40.3, 57.8, 55.4, 41.5, 47.6, 52.1],
    [105, 40.3, 0, 18.5, 23.9, 6, 11.8, 24.8],
    [123, 57.8, 18.5, 0, 13.9, 17.8, 18.3, 19.1],
    [130, 55.4, 23.9, 13.9, 0, 18.5, 30.4, 23.2],
    [106, 41.5, 6, 17.8, 18.5, 0, 8, 21.7],
    [109, 47.6, 11.8, 18.3, 30.4, 8, 0, 14.4],
    [113, 52.1, 24.8, 19.1, 23.2, 21.7, 14.4, 0]
])

# Hız matrisleri (12 saatlik zaman dilimi için, km/s)
np.random.seed(42)
hourly_speed_matrix = np.random.randint(60, 100, size=(8, 8, 12))

# Risk matrisleri (0-1 arası değerler, 12 zaman dilimi için)
hourly_risk_matrix = np.round(np.random.rand(8, 8, 12) * 0.5 + 0.25, 2)

# Yakıt tüketimi fonksiyonu (hıza bağlı)
def estimate_fuel_consumption(speed):
    return 0.3 + (90 - speed) * 0.005  # örnek tüketim modeli

# Yakıt tüketim matrisi (L/km)
fuel_consumption_matrix = np.zeros_like(hourly_speed_matrix, dtype=float)
for i in range(8):
    for j in range(8):
        for t in range(12):
            speed = hourly_speed_matrix[i, j, t]
            fuel_consumption_matrix[i, j, t] = estimate_fuel_consumption(speed)

# CO2 emisyonu katsayısı (kg/L)
co2_emission_factor = 2.31

# Servis süreleri (dakika)
service_times = {
    1: 30,
    2: 40,
    3: 32,
    4: 31,
    5: 33,
    6: 29,
    7: 20
}

# Zaman pencereleri (saat cinsinden)
time_windows = {
    1: (6, 18),
    2: (6, 18),
    3: (12, 18),
    4: (6, 18),
    5: (6, 12),
    6: (12, 18),
    7: (6, 12)
}

# Başlangıç saati
START_HOUR = 6
