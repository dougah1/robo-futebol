import streamlit as st
import random
import pandas as pd

st.title("⚽ Brasileirão Simulator 2026 - Modo Carreira")

# -----------------------------
# CONFIG INICIAL (2026 base fictícia)
# -----------------------------
SERIE_A = [
    "Flamengo","Palmeiras","São Paulo","Corinthians","Vasco",
    "Fluminense","Botafogo","Grêmio","Internacional","Atlético-MG",
    "Cruzeiro","Bahia","Fortaleza","Ceará","Bragantino",
    "Athletico-PR","Goiás","Vitória","Sport","Juventude"
]

SERIE_B = [
    "Santos","Coritiba","Cuiabá","Ponte Preta","Chapecoense",
    "Avaí","CRB","Vila Nova","Novorizontino","Operário"
]

# -----------------------------
# INIT ELO (persistente)
# -----------------------------
if "elo" not in st.session_state:
    st.session_state.elo = {t: random.randint(1600, 1850) for t in SERIE_A + SERIE_B}

if "ano" not in st.session_state:
    st.session_state.ano = 2026

# -----------------------------
# FUNÇÕES
# -----------------------------
def prob(a, b):
    return 1 / (1 + 10 ** ((b - a) / 400))

def gols(elo_a, elo_b):
    base_a = (elo_a / 1000) * 2.2
    base_b = (elo_b / 1000) * 2.2

    g1 = max(0, int(random.gauss(base_a, 1)))
    g2 = max(0, int(random.gauss(base_b, 1)))

    return g1, g2

# -----------------------------
# SIMULAÇÃO DE LIGA
# -----------------------------
def simular_liga(times, elo):

    tabela = {t: {"PTS":0,"GP":0,"GC":0,"SG":0} for t in times}

    for i in range(len(times)):
        for j in range(i+1, len(times)):

            a = times[i]
            b = times[j]

            ga, gb = gols(elo[a], elo[b])

            tabela[a]["GP"] += ga
            tabela[a]["GC"] += gb
            tabela[b]["GP"] += gb
            tabela[b]["GC"] += ga

            if ga > gb:
                tabela[a]["PTS"] += 3
            elif gb > ga:
                tabela[b]["PTS"] += 3
            else:
                tabela[a]["PTS"] += 1
                tabela[b]["PTS"] += 1

    for t in tabela:
        tabela[t]["SG"] = tabela[t]["GP"] - tabela[t]["GC"]

    df = pd.DataFrame.from_dict(tabela, orient="index")
    df = df.sort_values(["PTS","SG","GP"], ascending=False)

    return df

# -----------------------------
# EVOLUÇÃO ELO
# -----------------------------
def atualizar_elo(df):
    for i, row in df.iterrows():
        if row["PTS"] > 60:
            st.session_state.elo[i] += random.randint(10, 25)
        elif row["PTS"] < 45:
            st.session_state.elo[i] -= random.randint(10, 25)
        else:
            st.session_state.elo[i] += random.randint(-5, 10)

# -----------------------------
# PROMOÇÃO / REBAIXAMENTO
# -----------------------------
def troca_ligas(df_a, df_b):

    rebaixados = list(df_a.tail(4).index)
    promovidos = list(df_b.head(4).index)

    nova_a = list(df_a.head(16).index) + promovidos
    nova_b = list(df_b.tail(len(df_b)-4).index) + rebaixados

    return nova_a, nova_b, rebaixados, promovidos

# -----------------------------
# UI
# -----------------------------
st.write(f"📅 Ano atual: {st.session_state.ano}")

if st.button("Simular temporada completa"):

    st.subheader("🏆 Série A")

    df_a = simular_liga(SERIE_A, st.session_state.elo)

    st.dataframe(df_a)

    st.subheader("📉 Série B")

    df_b = simular_liga(SERIE_B, st.session_state.elo)

    st.dataframe(df_b)

    atualizar_elo(df_a)
    atualizar_elo(df_b)

    SERIE_A, SERIE_B, rebaixados, promovidos = troca_ligas(df_a, df_b)

    st.success(f"⬇️ Rebaixados: {rebaixados}")
    st.success(f"⬆️ Promovidos: {promovidos}")

    st.session_state.ano += 1

    st.info("🔥 Temporada finalizada! Clique novamente para próxima temporada.")
