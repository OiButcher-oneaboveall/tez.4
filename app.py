
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

with st.sidebar:
    st.header("⚙️ Optimizasyon Ayarları")
    pop_size = st.slider("Popülasyon Büyüklüğü", 50, 500, 100, 10)
    max_risk = st.slider("Maksimum Toplam Risk", 0.1, 2.0, 1.2, 0.1)
    generations = st.slider("Nesil Sayısı", 100, 2000, 300, 100)
    hedef = st.radio("Amaç Fonksiyonu", ["süre", "emisyon", "risk", "tümü"])
    hesapla = st.button("🚀 Rota Hesapla")

if hesapla:
    with st.spinner("En iyi rota hesaplanıyor..."):
        result = get_best_route(pop_size=pop_size, generations=generations, hedef=hedef, max_risk=max_risk)
        if result:
            st.session_state.sonuc = result
            st.session_state.show_results = True

if st.session_state.show_results and st.session_state.sonuc:
    tabs = st.tabs(["🗺️ Rota Haritası", "📊 Parametre Dağılımı", "📈 İstatistikler", "🎞️ Animasyonlu Harita", "📁 Senaryo Kaydet", "🕒 Gantt Şeması", "📊 Karşılaştırma"])
    route, total_time, total_fuel, total_co2, total_risk, log = st.session_state.sonuc

    tabs = st.tabs(["🗺️ Rota Haritası", "📊 Parametre Dağılımı", "📈 İstatistikler", "🎞️ Animasyonlu Harita", "📁 Senaryo Kaydet", "🕒 Gantt Şeması", "📊 Karşılaştırma"])

    with tabs[0]:
        st.subheader("🗺️ Rota Haritası")
        m = folium.Map(location=[41.0, 28.95], zoom_start=11)
        for i in range(len(route) - 1):
            c1, c2 = cities[route[i]], cities[route[i+1]]
            time = log[i]["travel_min"]
            label = f"{time} dk"
            folium.PolyLine(
                locations=[city_coords[c1], city_coords[c2]],
                tooltip=label,
                color='blue', weight=5, opacity=0.7
            ).add_to(m)
            folium.Marker(location=city_coords[c1], popup=c1).add_to(m)
        st_folium(m, width=900)

    with tabs[1]:
        st.subheader("📊 Parametre Dağılımları")
        risk_vals = hourly_risk_matrix.flatten()
        speed_vals = hourly_speed_matrix.flatten()
        fuel_vals = fuel_consumption_matrix.flatten()

        col1, col2 = st.columns(2)
        with col1:
            st.plotly_chart(px.histogram(x=risk_vals, nbins=30, title="Risk Dağılımı"), use_container_width=True)
            st.plotly_chart(px.histogram(x=speed_vals, nbins=30, title="Hız Dağılımı"), use_container_width=True)
        with col2:
            st.plotly_chart(px.box(x=fuel_vals, title="Yakıt Tüketimi Boxplot"), use_container_width=True)

    with tabs[2]:
        st.subheader("📈 Rota İstatistikleri")
        col1, col2, col3 = st.columns(3)
        col1.metric("Toplam Süre", f"{int(total_time)} dk")
        col2.metric("Toplam Emisyon", f"{total_co2:.2f} kg CO₂")
        col3.metric("Toplam Risk", f"{total_risk:.2f}")

        df_log = pd.DataFrame(log)
        st.dataframe(df_log, use_container_width=True)

    with tabs[3]:
        st.subheader("🎞️ Animasyonlu Rota")
        animated_map = create_animated_map(route, log)
        st_folium(animated_map, width=900)

elif not hesapla:
    st.info("Rota hesaplamak için lütfen '🚀 Rota Hesapla' butonuna basın.")


    with tabs[4]:
        st.subheader("📁 Kullanıcı Senaryo Kaydet")
        if "saved_scenarios" not in st.session_state:
            st.session_state.saved_scenarios = []
        scenario_name = st.text_input("Senaryo Adı Girin")
        if st.button("💾 Senaryoyu Kaydet"):
            st.session_state.saved_scenarios.append({
                "isim": scenario_name,
                "rota": route,
                "süre": total_time,
                "emisyon": total_co2,
                "risk": total_risk,
                "log": log
            })
            st.success(f"'{scenario_name}' senaryosu kaydedildi.")
        if st.session_state.saved_scenarios:
            st.write("📋 Kayıtlı Senaryolar:")
            st.dataframe(pd.DataFrame(st.session_state.saved_scenarios)[['isim', 'süre', 'emisyon', 'risk']])

    with tabs[5]:
        st.subheader("🕒 Gantt Zamanlama Şeması")
        gantt_df = []
        t = 0
        for i, entry in enumerate(log):
            start_min = t
            t += entry["travel_min"]
            travel_end = t
            if entry["wait"] > 0:
                t += entry["wait"]
                wait_end = t
                gantt_df.append(dict(Tip="Bekleme", Durak=entry["to"], Start=start_min, End=wait_end))
            if entry["service"] > 0:
                service_start = t
                t += entry["service"]
                gantt_df.append(dict(Tip="Servis", Durak=entry["to"], Start=service_start, End=t))
            gantt_df.append(dict(Tip="Yolculuk", Durak=entry["to"], Start=start_min, End=travel_end))
        gantt_df = pd.DataFrame(gantt_df)
        fig = px.timeline(gantt_df, x_start="Start", x_end="End", y="Durak", color="Tip", title="Gantt Zaman Çizelgesi")
        st.plotly_chart(fig, use_container_width=True)

    with tabs[6]:
        st.subheader("📊 Senaryo Karşılaştırma")
        if st.session_state.saved_scenarios:
            df = pd.DataFrame(st.session_state.saved_scenarios)
            fig = px.bar(df, x="isim", y=["süre", "emisyon", "risk"],
                         barmode="group", title="Senaryoların Karşılaştırması")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Henüz kayıtlı senaryo bulunmuyor.")
