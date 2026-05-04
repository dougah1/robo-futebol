import streamlit as st
import requests
import math
import unicodedata

st.title("🧠⚽ Bet Model PRO (Matemático Profissional)")

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"

headers = {
    "x-apisports-key": API_KEY
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
    url = f"https://v3.football.api-sports.io/teams?search={name}"
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    if not data.get("response"):
        return None

    return data["response"][0]["team"]["id"]

# -----------------------------
# MÉDIA DE GOLS (FORMA)
# -----------------------------
@st.cache_data
def form(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=10"
    r = requests.get(url, headers=headers, timeout=10)
    data = r.json()

    gf, gs = 0, 0

    for game in data.get("response", []):
        home = game["teams"]["home"]["id"]
        goals = game["goals"]

        if home == team_id:
            gf += goals["home"] or 0
            gs += goals["away"] or 0
        else:
            gf += goals["away"] or 0
            gs += goals["home"] or 0

    return gf / 10, gs / 10

# -----------------------------
# POISSON
# -----------------------------
def poisson(lmbda, k):
    return (math.exp(-lmbda) * (lmbda ** k)) / math.factorial(k)

# -----------------------------
# MATRIZ DE RESULTADOS
# -----------------------------
def match_probs(lambda_a, lambda_b, max_goals=5):

    home_win = 0
    draw = 0
    away_win = 0
    over25 = 0
    btts = 0

    total = 0

    for i in range(max_goals + 1):
        for j in range(max_goals + 1):

            p = poisson(lambda_a, i) * poisson(lambda_b, j)
            total += p

            # resultado
            if i > j:
                home_win += p
            elif i < j:
                away_win += p
            else:
                draw += p

            # over 2.5
            if i + j >= 3:
                over25 += p

            # ambas marcam
            if i > 0 and j > 0:
                btts += p

    return (
        home_win / total * 100,
        draw / total * 100,
        away_win / total * 100,
        over25 / total * 100,
        btts / total * 100
    )

# -----------------------------
# UI
# -----------------------------
team_a = st.text_input("Time Casa")
team_b = st.text_input("Time Fora")

if st.button("Calcular probabilidade profissional"):

    a_id = get_team_id(team_a)
    b_id = get_team_id(team_b)

    if not a_id or not b_id:
        st.error("Time não encontrado")
        st.stop()

    a_att, a_def = form(a_id)
    b_att, b_def = form(b_id)

    # EXPECTATIVA DE GOLS (modelo básico correto)
    lambda_a = max(0.2, a_att - b_def + 1.3)
    lambda_b = max(0.2, b_att - a_def + 1.3)

    home, draw, away, over25, btts = match_probs(lambda_a, lambda_b)

    st.subheader("📊 Probabilidades (modelo matemático real)")

    st.write(f"{team_a} vitória: {home:.2f}%")
    st.write(f"Empate: {draw:.2f}%")
    st.write(f"{team_b} vitória: {away:.2f}%")

    st.subheader("📈 Mercados adicionais")

    st.write(f"Over 2.5 gols: {over25:.2f}%")
    st.write(f"Ambas marcam (BTTS): {btts:.2f}%")
