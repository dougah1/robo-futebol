import streamlit as st
import requests
import random

st.title("💰⚽ Bet Simulator PRO (Tempo Real)")

# 🔑 COLE SUA API KEY AQUI
API_KEY = "0c5168f1172dbcbe953972986f7aa11a"

headers = {
    "x-apisports-key": API_KEY
}

# -----------------------------
# BUSCAR ID DO TIME
# -----------------------------
def get_team_id(name):
    url = f"https://v3.football.api-sports.io/teams?search={name}"
    r = requests.get(url, headers=headers)
    data = r.json()
    return data["response"][0]["team"]["id"]

# -----------------------------
# ÚLTIMOS JOGOS (FORMA REAL)
# -----------------------------
def form(team_id):
    url = f"https://v3.football.api-sports.io/fixtures?team={team_id}&last=5"
    r = requests.get(url, headers=headers)
    data = r.json()

    gf = 0
    gs = 0

    for game in data["response"]:
        home = game["teams"]["home"]["id"]
        goals = game["goals"]

        if home == team_id:
            gf += goals["home"]
            gs += goals["away"]
        else:
            gf += goals["away"]
            gs += goals["home"]

    return gf/5, gs/5

# -----------------------------
# POISSON SIMPLES
# -----------------------------
def poisson(lmbda):
    return max(0, int(random.gauss(lmbda, 1)))

# -----------------------------
# SIMULAÇÃO
# -----------------------------
def simulate(a_id, b_id):

    a_att, a_def = form(a_id)
    b_att, b_def = form(b_id)

    exp_a = max(0.2, a_att - b_def + 1.2)
    exp_b = max(0.2, b_att - a_def + 1.2)

    ga = poisson(exp_a)
    gb = poisson(exp_b)

    total = ga + gb + 1

    pa = (ga / total) * 100
    pb = (gb / total) * 100
    draw = 100 - (pa + pb)

    return ga, gb, pa, draw, pb

# -----------------------------
# ODDS
# -----------------------------
def odds(prob):
    return round(100 / prob, 2)

# -----------------------------
# VALUE BET
# -----------------------------
def value(prob, odd):
    return prob > (100 / odd)

# -----------------------------
# UI
# -----------------------------
team_a = st.text_input("Time Casa")
team_b = st.text_input("Time Fora")

if st.button("Analisar"):

    try:
        a_id = get_team_id(team_a)
        b_id = get_team_id(team_b)

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

    except Exception as e:
        st.error("Erro ao buscar dados. Verifique os nomes dos times.")
