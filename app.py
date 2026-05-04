import streamlit as st
import requests
import math
import unicodedata

st.title("⚽🧠 Bet Model HÍBRIDO (Profissional Correto)")

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"
headers = {
    "x-apisports-key": API_KEY
}

# -----------------------------
# ELO BASE (FORÇA HISTÓRICA FIXA)
# -----------------------------
elo_base = {
    "Palmeiras": 1850,
    "Flamengo": 1840,
    "Atlético-MG": 1800,
    "São Paulo": 1760,
    "Corinthians": 1740,
    "Grêmio": 1750,
    "Internacional": 1760,
    "Fluminense": 1770,
    "Botafogo": 1780,
    "Bragantino": 1750,
    "Vasco": 1650,
    "Cruzeiro": 1700,
    "Bahia": 1680,
    "Fortaleza": 1720,
    "Ceará": 1670,
    "Athletico-PR": 1760,
    "Goiás": 1600,
    "Sport": 1620,
    "Vitória": 1630,
    "Juventude": 1600,
    "Remo": 1500  # 👈 evita absurdo tipo favorito contra Palmeiras
}

# -----------------------------
# BUSCAR TIME
# -----------------------------
@st.cache_data
def get_team_id(name):
    url = f"https://v3.football.api-sports.io/teams?search={name}"
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    if not data.get("response"):
        return None

    return data["response"][0]["team"]["id"]

# -----------------------------
# FORMA (ÚLTIMOS 10 JOGOS)
# -----------------------------
@st.cache_data
def form(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    gf, gs = 0, 0
    jogos = 0

    for g in data.get("response", []):
        home = g["teams"]["home"]["id"]
        goals = g["goals"]

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

# -----------------------------
# POISSON
# -----------------------------
def poisson(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

# -----------------------------
# PROBABILIDADE COMPLETA
# -----------------------------
def match_prob(lh, la):

    home = 0
    draw = 0
    away = 0

    for i in range(6):
        for j in range(6):

            p = poisson(lh, i) * poisson(la, j)

            if i > j:
                home += p
            elif i == j:
                draw += p
            else:
                away += p

    total = home + draw + away

    return (
        home / total * 100,
        draw / total * 100,
        away / total * 100
    )

# -----------------------------
# UI
# -----------------------------
team_a = st.text_input("Time Casa")
team_b = st.text_input("Time Fora")

if st.button("Calcular probabilidade híbrida"):

    a_id = get_team_id(team_a)
    b_id = get_team_id(team_b)

    if not a_id or not b_id:
        st.error("Time não encontrado")
        st.stop()

    # -----------------------------
    # FORÇA HISTÓRICA (ELO)
    # -----------------------------
    base_a = elo_base.get(team_a, 1650)
    base_b = elo_base.get(team_b, 1650)

    # -----------------------------
    # FORMA RECENTE
    # -----------------------------
    a_att, a_def = form(a_id)
    b_att, b_def = form(b_id)

    # -----------------------------
    # NORMALIZAÇÃO HÍBRIDA (CHAVE DO MODELO)
    # -----------------------------
    strength_a = (base_a * 0.7) + ((a_att * 1000) * 0.3)
    strength_b = (base_b * 0.7) + ((b_att * 1000) * 0.3)

    # -----------------------------
    # EXPECTATIVA DE GOLS
    # -----------------------------
    league_avg = 1.35
    home_adv = 1.12

    lambda_a = league_avg * (strength_a / strength_b) * home_adv
    lambda_b = league_avg * (strength_b / strength_a)

    # -----------------------------
    # RESULTADO FINAL
    # -----------------------------
    home, draw, away = match_prob(lambda_a, lambda_b)

    st.subheader("📊 Probabilidade híbrida (REALISTA)")

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
