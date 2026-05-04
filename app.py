import streamlit as st
import requests

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"
API_HOST = "api-football-v1.p.rapidapi.com"

st.title("⚽ Robô PRO (Modo Estável)")

times = {
    "Flamengo": 127,
    "Palmeiras": 121,
    "São Paulo": 133,
    "Corinthians": 119,
    "Remo": 5583
}

def buscar_stats(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {
        "team": team_id,
        "league": 71,
        "season": 2024
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "response" in data and data["response"]:
            gols = data["response"]["goals"]["for"]["total"]["total"]
            sofridos = data["response"]["goals"]["against"]["total"]["total"]
            return gols, sofridos
        else:
            return 0, 0

    except:
        return 0, 0


time_a = st.selectbox("Time A", list(times.keys()))
time_b = st.selectbox("Time B", list(times.keys()))

if st.button("Analisar"):

    id_a = times[time_a]
    id_b = times[time_b]

    gols_a, sofridos_a = buscar_stats(id_a)
    gols_b, sofridos_b = buscar_stats(id_b)

    forca_a = gols_a - sofridos_a
    forca_b = gols_b - sofridos_b

    total = abs(forca_a) + abs(forca_b)

    if total == 0:
        st.warning("API não retornou dados hoje (limite atingido).")
    else:
        prob_a = (abs(forca_a) / total) * 100
        prob_b = (abs(forca_b) / total) * 100
        empate = 100 - (prob_a + prob_b)

        st.subheader("📊 Probabilidades")

        st.success(f"{time_a}: {prob_a:.1f}%")
        st.info(f"Empate: {empate:.1f}%")
        st.success(f"{time_b}: {prob_b:.1f}%")
