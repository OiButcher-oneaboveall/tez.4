
import folium
import openrouteservice
from folium.plugins import BeautifyIcon
from data_config import city_coords, cities

# OpenRouteService API istemcisi (anahtar kullanıcıdan alınmalı)
ORS_API_KEY = "your_openrouteservice_api_key"
client = openrouteservice.Client(key=ORS_API_KEY)

def get_route_polyline(coord1, coord2):
    try:
        coords = (coord1[::-1], coord2[::-1])  # folium: [lat, lon] -> ORS: [lon, lat]
        route = client.directions(coords, profile='driving-car', format='geojson')
        geometry = route['features'][0]['geometry']['coordinates']
        return [(lat, lon) for lon, lat in geometry]
    except Exception:
        return [coord1, coord2]

def create_animated_map(route, log):
    m = folium.Map(location=[41.0, 28.95], zoom_start=11)
    named_route = [cities[i] for i in route]

    folium.Marker(
        location=city_coords[named_route[0]],
        icon=folium.Icon(color='green'),
        popup="Başlangıç: " + named_route[0]
    ).add_to(m)

    for i in range(len(named_route) - 1):
        from_city = named_route[i]
        to_city = named_route[i+1]
        from_coord = city_coords[from_city]
        to_coord = city_coords[to_city]
        travel_time = log[i]['travel_min'] if i < len(log) else "?"
        label = f"{travel_time} dk"

        line = get_route_polyline(from_coord, to_coord)
        folium.PolyLine(
            locations=line,
            tooltip=label,
            color='blue', weight=5, opacity=0.8
        ).add_to(m)

        folium.Marker(
            location=to_coord,
            popup=f"{i+1}. Nokta: {to_city}",
            icon=BeautifyIcon(
                icon="arrow-down", icon_shape="marker", number=i+1, spin=False, text_color="#fff"
            )
        ).add_to(m)

    return m
