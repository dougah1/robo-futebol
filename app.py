import streamlit as st
import requests
import math
import unicodedata

st.title("🧠⚽ Bet Model PRO (Final Profissional)")

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"

headers = {
    "x-apisports-key": API_KEY
}

# -----------------------------
# NORMALIZAR TEXTO
# -----------------------------
def normalize(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# -----------------------------
# BUSCAR TIME
# -----------------------------
@st.cache_data
def get_team_id(name):
    try:
        url = f"https://v3.football.api-sports.io/teams?search={name}"
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        if not data.get("response"):
            return None

        return data["response"][0]["team"]["id"]

    except:
        return None

# -----------------------------
# FORMA (ÚLTIMOS 10 JOGOS)
# -----------------------------
@st.cache_data
def form(team_id):
    try:
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        gf = 0
        gs = 0
        jogos = 0

        for game in data.get("response", []):
            home = game["teams"]["home"]["id"]
            goals = game["goals"]

            if home == team_id:
                gf += goals["home"] or 0
                gs += goals["away"] or 0
            else:
                gf += goals["away"] or 0
                gs += goals["home"] or 0

            jogos += 1

        if jogos == 0:
            return 1.2, 1.2

        return gf / jogos, gs / jogos

    except:
        return 1.2, 1.2

# -----------------------------
# POISSON
# -----------------------------
def poisson(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

# -----------------------------
# PROBABILIDADE COMPLETA
# -----------------------------
def match_prob(lambda_home, lambda_away, max_goals=6):

    home_win = 0
    draw = 0
    away_win = 0
    total = 0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):

            p = poisson(lambda_home, i) * poisson(lambda_away, j)
            total += p

            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p

    return (
        home_win / total * 100,
        draw / total * 100,
        away_win / total * 100
    )

# -----------------------------
# UI
# -----------------------------
team_a = st.text_input("Time Casa")
team_b = st.text_input("Time Fora")

if st.button("Calcular probabilidade"):

    a_id = get_team_id(team_a)
    b_id = get_team_id(team_b)

    if not a_id or not b_id:
        st.error("❌ Time não encontrado. Use nomes simples como Flamengo, Palmeiras, Corinthians.")
        st.stop()

    # FORMA REAL
    a_att, a_def = form(a_id)
    b_att, b_def = form(b_id)

    # -----------------------------
    # MODELO CORRETO (CHAVE DO SISTEMA)
    # -----------------------------
    league_avg = 1.35
    home_adv = 1.12

    attack_a = a_att / (b_def + 0.3)
    attack_b = b_att / (a_def + 0.3)

    lambda_a = league_avg * attack_a * home_adv
    lambda_b = league_avg * attack_b

    # -----------------------------
    # PROBABILIDADES
    # -----------------------------
    home, draw, away = match_prob(lambda_a, lambda_b)

    st.subheader("📊 Probabilidades (modelo profissional)")

    st.write(f"{team_a}: {home:.2f}%")
    st.write(f"Empate: {draw:.2f}%")
    st.write(f"{team_b}: {away:.2f}%")

    st.subheader("🧠 Leitura do modelo")

    if home > away and home > draw:
        st.success(f"Favorito: {team_a}")
    elif away > home and away > draw:
        st.success(f"Favorito: {team_b}")
    else:
        st.info("Jogo equilibrado")
