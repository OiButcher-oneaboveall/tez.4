
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px

from optimizer import get_best_route
from data_config import cities, city_coords, hourly_risk_matrix, hourly_speed_matrix, fuel_consumption_matrix
from visualizer import create_animated_map

st.set_page_config(layout="wide", page_title="Akıllı Rota Planlayıcı")
st.title("🚛 Akıllı ve Sürdürülebilir Rota Planlayıcı")

if "show_results" not in st.session_state:
    st.session_state.show_results = False
    st.session_state.sonuc = None
    st.session_state.saved_scenarios = []

with st.sidebar:
    st.header("⚙️ Optimizasyon Ayarları")
    pop_size = st.slider("Popülasyon Büyüklüğü", 50, 300, 100, 10)
    generations = st.slider("Nesil Sayısı", 100, 1000, 300, 100)
    max_risk = st.slider("Maksimum Toplam Risk", 0.1, 2.0, 1.2, 0.1)
    hedef = st.radio("Amaç Fonksiyonu", ["süre", "emisyon", "risk", "tümü"])
    hesapla = st.button("🚀 Rota Hesapla")

if hesapla:
    with st.spinner("En iyi rota hesaplanıyor..."):
        result = get_best_route(pop_size=pop_size, generations=generations, hedef=hedef, max_risk=max_risk)
        if result:
            st.session_state.sonuc = result
            st.session_state.show_results = True
        else:
            st.error("Hiçbir geçerli rota bulunamadı. Lütfen risk sınırını veya nesil sayısını artırın.")

if st.session_state.show_results and st.session_state.sonuc:
    route, total_time, total_fuel, total_co2, total_risk, log = st.session_state.sonuc

    tabs = st.tabs(["🗺️ Harita", "📊 Dağılım", "📈 İstatistik", "🎞️ Animasyon", "📁 Kaydet", "🕒 Gantt", "📊 Karşılaştırma"])

    with tabs[0]:
        m = folium.Map(location=[41.0, 28.95], zoom_start=11)
        for i in range(len(route) - 1):
            c1, c2 = cities[route[i]], cities[route[i+1]]
            folium.PolyLine([city_coords[c1], city_coords[c2]], color='blue').add_to(m)
            folium.Marker(location=city_coords[c1], popup=c1).add_to(m)
        st_folium(m, width=800)

    with tabs[1]:
        st.plotly_chart(px.histogram(x=hourly_risk_matrix.flatten(), nbins=30, title="Risk Dağılımı"), use_container_width=True)

    with tabs[2]:
        st.metric("Toplam Süre", f"{int(total_time)} dk")
        st.metric("Toplam Emisyon", f"{total_co2:.2f} kg CO₂")
        st.metric("Toplam Risk", f"{total_risk:.2f}")
        st.dataframe(pd.DataFrame(log))

    with tabs[3]:
        st_folium(create_animated_map(route, log), width=800)

    with tabs[4]:
        ad = st.text_input("Senaryo Adı")
        if st.button("💾 Kaydet"):
            st.session_state.saved_scenarios.append({
                "isim": ad, "süre": total_time, "emisyon": total_co2, "risk": total_risk
            })
            st.success("Senaryo kaydedildi.")
        if st.session_state.saved_scenarios:
            st.dataframe(pd.DataFrame(st.session_state.saved_scenarios))

    with tabs[5]:
        st.info("Gantt şeması burada olacak (örnek).")

    with tabs[6]:
        if st.session_state.saved_scenarios:
            df = pd.DataFrame(st.session_state.saved_scenarios)
            st.plotly_chart(px.bar(df, x="isim", y=["süre", "emisyon", "risk"], barmode="group"), use_container_width=True)

elif not hesapla:
    st.info("🚀 Lütfen rota hesaplayın.")
