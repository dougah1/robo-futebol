import streamlit as st
import requests

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"
API_HOST = "api-football-v1.p.rapidapi.com"

st.title("⚽ Robô PRO - Previsão de Jogos")

def buscar_time(nome):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {"search": nome}

    try:
        response = requests.get(url, headers=headers, params=params)
        data = response.json()

        if "response" in data and len(data["response"]) > 0:
            return data["response"][0]["team"]["id"]
        else:
            st.error(f"Time '{nome}' não encontrado ou API limitou.")
            return None

    except:
        st.error("Erro ao conectar com API.")
        return None


def buscar_stats(team_id):
    url = "https://api-football-v1.p.rapidapi.com/v3/teams/statistics"
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST
    }
    params = {
        "team": team_id,
        "league": 71,   # Brasileirão
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
            st.warning("Não foi possível pegar estatísticas.")
            return 0, 0

    except:
        st.error("Erro ao buscar estatísticas.")
        return 0, 0


time_a = st.text_input("Time A")
time_b = st.text_input("Time B")

if st.button("Analisar"):

    if not time_a or not time_b:
        st.warning("Digite os dois times!")
    else:
        id_a = buscar_time(time_a)
        id_b = buscar_time(time_b)

        if id_a and id_b:

            gols_a, sofridos_a = buscar_stats(id_a)
            gols_b, sofridos_b = buscar_stats(id_b)

            forca_a = gols_a - sofridos_a
            forca_b = gols_b - sofridos_b

            total = abs(forca_a) + abs(forca_b)

            if total == 0:
                st.warning("Dados insuficientes pra prever.")
            else:
                prob_a = (abs(forca_a) / total) * 100
                prob_b = (abs(forca_b) / total) * 100
                empate = 100 - (prob_a + prob_b)

                st.subheader("📊 Probabilidades")

                st.success(f"{time_a}: {prob_a:.1f}%")
                st.info(f"Empate: {empate:.1f}%")
                st.success(f"{time_b}: {prob_b:.1f}%")
