import streamlit as st
import requests
import random
import unicodedata

st.title("🛡️💰 Bet Simulator PRO (Blindado + Tempo Real)")

API_KEY = "0c5168f1172dbcbe953972986f7aa11a"

headers = {
    "x-apisports-key": API_KEY
}

# -----------------------------
# NORMALIZA TEXTO
# -----------------------------
def normalize(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    ).lower()

# -----------------------------
# BUSCAR TIME (SEGURO)
# -----------------------------
@st.cache_data
def get_team_id(name):
    try:
        url = f"https://v3.football.api-sports.io/teams?search={name}"
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        if "response" not in data or len(data["response"]) == 0:
            return None

        return data["response"][0]["team"]["id"]

    except:
        return None

# -----------------------------
# FORMA (ÚLTIMOS 5 JOGOS)
# -----------------------------
@st.cache_data
def form(team_id):

    try:
        url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()

        if "response" not in data:
            return 1.0, 1.0

        gf = 0
        gs = 0

        for game in data["response"]:
            home = game["teams"]["home"]["id"]
            goals = game["goals"]

            if home == team_id:
                gf += goals["home"] or 0
                gs += goals["away"] or 0
            else:
                gf += goals["away"] or 0
                gs += goals["home"] or 0

        return gf / 5, gs / 5

    except:
        return 1.0, 1.0

# -----------------------------
# POISSON SIMPLES
# -----------------------------
def poisson(lmbda):
    return max(0, int(random.gauss(lmbda, 1)))

# -----------------------------
# SIMULAÇÃO DE JOGO
# -----------------------------
def simulate(a_id, b_id):

    a_att, a_def = form(a_id)
    b_att, b_def = form(b_id)

    exp_a = max(0.2, a_att - b_def + 1.2)
    exp_b = max(0.2, b_att - a_def + 1.2)

    ga = poisson(exp_a)
    gb = poisson(exp_b)

    total = max(ga + gb, 1)  # 🔥 FIX IMPORTANTE

    pa = (ga / total) * 100
    pb = (gb / total) * 100
    draw = 100 - (pa + pb)

    return ga, gb, pa, draw, pb

# -----------------------------
# ODDS (BLINDADO)
# -----------------------------
def odds(prob):
    try:
        if prob is None or prob <= 0:
            return 99.99
        return round(100 / prob, 2)
    except:
        return 99.99

# -----------------------------
# VALUE BET
# -----------------------------
def value(prob, odd):
    try:
        return prob > (100 / odd)
    except:
        return False

# -----------------------------
# UI
# -----------------------------
team_a = st.text_input("Time Casa")
team_b = st.text_input("Time Fora")

if st.button("Analisar aposta"):

    if not team_a or not team_b:
        st.error("Digite os dois times")
        st.stop()

    team_a_clean = normalize(team_a)
    team_b_clean = normalize(team_b)

    a_id = get_team_id(team_a_clean)
    b_id = get_team_id(team_b_clean)

    if a_id is None or b_id is None:
        st.error("❌ Time não encontrado. Use nomes como: Flamengo, Palmeiras, Corinthians, São Paulo")
        st.stop()

    ga, gb, pa, draw, pb = simulate(a_id, b_id)

    st.subheader("📊 Probabilidades")
    st.write(f"{team_a}: {pa:.1f}%")
    st.write(f"Empate: {draw:.1f}%")
    st.write(f"{team_b}: {pb:.1f}%")

    st.subheader("🎯 Placar provável")
    st.write(f"{team_a} {ga} x {gb} {team_b}")

    st.subheader("💰 Odds justas")

    oa = odds(pa)
    od = odds(draw)
    ob = odds(pb)

    st.write(f"{team_a}: {oa}")
    st.write(f"Empate: {od}")
    st.write(f"{team_b}: {ob}")

    st.subheader("🔥 Value Bet")

    st.write(f"{team_a}: {'SIM' if value(pa, oa) else 'NÃO'}")
    st.write(f"Empate: {'SIM' if value(draw, od) else 'NÃO'}")
    st.write(f"{team_b}: {'SIM' if value(pb, ob) else 'NÃO'}")
