import streamlit as st
import requests

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"
API_HOST = "api-football-v1.p.rapidapi.com"

st.title("⚽ Robô PRO com Dados Reais")

def buscar_time(nome):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {"search": nome}

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data["response"]:
        return data["response"][0]["team"]["id"]
    return None

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

    response = requests.get(url, headers=headers, params=params)
    data = response.json()

    if data["response"]:
        gols = data["response"]["goals"]["for"]["total"]["total"]
        sofridos = data["response"]["goals"]["against"]["total"]["total"]
        return gols, sofridos

    return 0, 0

time_a = st.text_input("Time A")
time_b = st.text_input("Time B")

if st.button("Analisar"):

    if time_a and time_b:

        id_a = buscar_time(time_a)
        id_b = buscar_time(time_b)

        if id_a and id_b:

            gols_a, sofridos_a = buscar_stats(id_a)
            gols_b, sofridos_b = buscar_stats(id_b)

            forca_a = gols_a - sofridos_a
            forca_b = gols_b - sofridos_b

            total = abs(forca_a) + abs(forca_b)

            prob_a = (abs(forca_a) / total) * 100
            prob_b = (abs(forca_b) / total) * 100
            empate = 100 - (prob_a + prob_b)

            st.subheader("📊 Probabilidades reais")

            st.write(f"{time_a}: {prob_a:.1f}%")
            st.write(f"Empate: {empate:.1f}%")
            st.write(f"{time_b}: {prob_b:.1f}%")

        else:
            st.error("Time não encontrado!")

    else:
        st.warning("Digite os dois times!")
