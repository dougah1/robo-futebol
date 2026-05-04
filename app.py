import streamlit as st
import requests
import math

st.title("⚽🧠 Probabilidade Real de Futebol (Modelo Estatístico)")

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"

headers = {
    "x-apisports-key": API_KEY
}

# -----------------------------
# TIME ID
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
# ESTATÍSTICA REAL (GOLS)
# -----------------------------
@st.cache_data
def team_stats(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    gf, gs, n = 0, 0, 0

    for g in data.get("response", []):
        home = g["teams"]["home"]["id"]
        goals = g["goals"]

        if home == team_id:
            gf += goals["home"] or 0
            gs += goals["away"] or 0
        else:
            gf += goals["away"] or 0
            gs += goals["home"] or 0

        n += 1

    if n == 0:
        return 1.2, 1.2

    return gf / n, gs / n

# -----------------------------
# POISSON
# -----------------------------
def poisson(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

# -----------------------------
# PROBABILIDADE COMPLETA
# -----------------------------
def probabilities(lh, la):

    home, draw, away = 0, 0, 0
    over25, btts = 0, 0

    for i in range(7):
        for j in range(7):

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

    total = home + draw + away

    return (
        home / total * 100,
        draw / total * 100,
        away / total * 100,
        over25 / total * 100,
        btts / total * 100
    )

# -----------------------------
# UI
# -----------------------------
team_a = st.text_input("Time Casa")
team_b = st.text_input("Time Fora")

if st.button("Calcular probabilidade real"):

    a_id = get_team_id(team_a)
    b_id = get_team_id(team_b)

    if not a_id or not b_id:
        st.error("Time não encontrado")
        st.stop()

    # estatísticas reais
    a_att, a_def = team_stats(a_id)
    b_att, b_def = team_stats(b_id)

    # média da liga (normalização)
    league_avg = 1.35
    home_adv = 1.10

    # EXPECTATIVA DE GOLS (MODELO CORRETO)
    lambda_home = league_avg * (a_att / b_def) * home_adv
    lambda_away = league_avg * (b_att / a_def)

    # resultados
    home, draw, away, over25, btts = probabilities(lambda_home, lambda_away)

    st.subheader("📊 Probabilidade 1X2 (REAL ESTATÍSTICA)")

    st.write(f"{team_a}: {home:.2f}%")
    st.write(f"Empate: {draw:.2f}%")
    st.write(f"{team_b}: {away:.2f}%")

    st.subheader("📈 Mercados adicionais")

    st.write(f"Over 2.5 gols: {over25:.2f}%")
    st.write(f"Ambas marcam: {btts:.2f}%")

    st.subheader("🧠 Interpretação")

    if home > away and home > draw:
        st.success(f"Favorito: {team_a}")
    elif away > home and away > draw:
        st.success(f"Favorito: {team_b}")
    else:
        st.info("Jogo equilibrado")
