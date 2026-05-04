import streamlit as st
import requests
import math
import unicodedata

st.title("⚽🧠 Bet Model HÍBRIDO PRO (Brasileirão 2026)")

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"

headers = {
    "x-apisports-key": API_KEY
}

# -----------------------------
# ELO BASE (BRASILEIRÃO 2026)
# -----------------------------
elo_base = {
    "Athletico-PR": 1760,
    "Atlético-MG": 1800,
    "Bahia": 1680,
    "Botafogo": 1780,
    "Chapecoense": 1600,
    "Corinthians": 1740,
    "Coritiba": 1650,
    "Cruzeiro": 1700,
    "Flamengo": 1840,
    "Fluminense": 1770,
    "Grêmio": 1750,
    "Internacional": 1760,
    "Mirassol": 1580,
    "Palmeiras": 1850,
    "Red Bull Bragantino": 1750,
    "Remo": 1500,
    "Santos": 1730,
    "São Paulo": 1760,
    "Vasco": 1650,
    "Vitória": 1630,

    # Série B (extra)
    "América-MG": 1700,
    "Atlético-GO": 1670,
    "Ceará": 1670,
    "Fortaleza": 1720,
    "Goiás": 1600,
    "Juventude": 1600,
    "Sport": 1620
}

# -----------------------------
# NORMALIZAÇÃO
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
# FORMA (10 JOGOS)
# -----------------------------
@st.cache_data
def form(team_id):
    try:
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        gf, gs, jogos = 0, 0, 0

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

    except:
        return 1.2, 1.2

# -----------------------------
# POISSON
# -----------------------------
def poisson(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

# -----------------------------
# MODELO COMPLETO
# -----------------------------
def match_model(lh, la):

    home, draw, away = 0, 0, 0
    over25, btts = 0, 0
    best_score = (0, 0)
    best_p = 0

    for i in range(6):
        for j in range(6):

            p = poisson(lh, i) * poisson(la, j)

            if i > j:
                home += p
            elif i == j:
                draw += p
            else:
                away += p

            if i + j >= 3:
                over25 += p

            if i > 0 and j > 0:
                btts += p

            if p > best_p:
                best_p = p
                best_score = (i, j)

    total = home + draw + away

    return (
        home / total * 100,
        draw / total * 100,
        away / total * 100,
        over25 / total * 100,
        btts / total * 100,
        best_score
    )

# -----------------------------
# UI
# -----------------------------
team_a = st.text_input("Time Casa")
team_b = st.text_input("Time Fora")

if st.button("Analisar jogo"):

    a_id = get_team_id(team_a)
    b_id = get_team_id(team_b)

    if not a_id or not b_id:
        st.error("❌ Time não encontrado na API")
        st.stop()

    # força base
    base_a = elo_base.get(team_a, 1650)
    base_b = elo_base.get(team_b, 1650)

    # forma
    a_att, a_def = form(a_id)
    b_att, b_def = form(b_id)

    # híbrido real
    strength_a = (base_a * 0.7) + (a_att * 1000 * 0.3)
    strength_b = (base_b * 0.7) + (b_att * 1000 * 0.3)

    league_avg = 1.35
    home_adv = 1.12

    lambda_a = league_avg * (strength_a / strength_b) * home_adv
    lambda_b = league_avg * (strength_b / strength_a)

    # resultado
    home, draw, away, over25, btts, score = match_model(lambda_a, lambda_b)

    st.subheader("📊 Probabilidades 1X2")
    st.write(f"{team_a}: {home:.2f}%")
    st.write(f"Empate: {draw:.2f}%")
    st.write(f"{team_b}: {away:.2f}%")

    st.subheader("🎯 Placar mais provável")
    st.write(f"{team_a} {score[0]} x {score[1]} {team_b}")

    st.subheader("📈 Mercados")
    st.write(f"Over 2.5 gols: {over25:.2f}%")
    st.write(f"Ambas marcam: {btts:.2f}%")

    st.subheader("🧠 Leitura do modelo")

    if home > away and home > draw:
        st.success(f"Favorito: {team_a}")
    elif away > home and away > draw:
        st.success(f"Favorito: {team_b}")
    else:
        st.info("Jogo equilibrado")
