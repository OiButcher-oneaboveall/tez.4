
import plotly.express as px
import streamlit as st

def plot_risk_vs_time(df):
    fig = px.line(df, x="Risk Sınırı", y="Toplam Süre", markers=True,
                  title="Risk Sınırı ile Süre Arasındaki Duyarlılık")
    st.plotly_chart(fig, use_container_width=True)

def plot_speed_sensitivity(df):
    fig = px.bar(df, x="Hız Katsayısı", y="Toplam Süre", text_auto=True,
                 title="Hız Değişiminin Toplam Süreye Etkisi")
    st.plotly_chart(fig, use_container_width=True)

def plot_risk_distribution(log):
    risk_values = [entry["risk"] for entry in log]
    fig = px.pie(names=[entry["to"] for entry in log], values=risk_values,
                 title="Ziyaret Edilen Düğümlere Göre Risk Dağılımı")
    st.plotly_chart(fig, use_container_width=True)
