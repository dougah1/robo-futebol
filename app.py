import streamlit as st
import math

st.set_page_config(page_title="Robô de Análise Futebol", layout="centered")

st.title("⚽ Robô BRABO de Análise de Jogos")

st.markdown("Digite os dados dos times:")

# INPUTS
st.subheader("Time A")
forma_a = st.number_input("Pontos últimos 5 jogos (0 a 15)", 0, 15, 10)
gols_a = st.number_input("Média de gols marcados", 0.0, 5.0, 1.5)
sofridos_a = st.number_input("Média de gols sofridos", 0.0, 5.0, 1.0)
mando_a = st.selectbox("Joga em casa?", ["Sim", "Não"])

st.subheader("Time B")
forma_b = st.number_input("Pontos últimos 5 jogos ", 0, 15, 7)
gols_b = st.number_input("Média de gols marcados ", 0.0, 5.0, 1.2)
sofridos_b = st.number_input("Média de gols sofridos ", 0.0, 5.0, 1.3)
mando_b = st.selectbox("Joga em casa? ", ["Sim", "Não"])

def calcular_forca(forma, gols, sofridos, mando):
    ataque = gols
    defesa = 1 / (sofridos + 0.1)
    mando_val = 1 if mando == "Sim" else 0

    return (forma * 0.4) + (ataque * 0.3) + (defesa * 0.2) + (mando_val * 0.1)

def poisson(lmbda, k):
    return (lmbda**k * math.exp(-lmbda)) / math.factorial(k)

if st.button("Analisar Jogo"):

    forca_a = calcular_forca(forma_a, gols_a, sofridos_a, mando_a)
    forca_b = calcular_forca(forma_b, gols_b, sofridos_b, mando_b)

    total = forca_a + forca_b

    prob_a = forca_a / total
    prob_b = forca_b / total
    empate = 1 - (prob_a + prob_b) * 0.9

    st.subheader("📊 Probabilidades")

    st.write(f"🏆 Time A: {prob_a*100:.1f}%")
    st.write(f"🤝 Empate: {empate*100:.1f}%")
    st.write(f"🏆 Time B: {prob_b*100:.1f}%")

    # POISSON GOLS
    media_a = gols_a
    media_b = gols_b

    gols_probs = {}

    for i in range(5):
        for j in range(5):
            prob = poisson(media_a, i) * poisson(media_b, j)
            gols_probs[f"{i}x{j}"] = prob

    placar = max(gols_probs, key=gols_probs.get)

    st.subheader("🎯 Placar mais provável")
    st.write(placar)

    st.subheader("🔥 Sugestões")

    if media_a + media_b > 2.5:
        st.write("✔ Over 2.5 gols")
    else:
        st.write("⚠️ Under 2.5 gols")

    if gols_a > 1 and gols_b > 1:
        st.write("✔ Ambos marcam")

    if prob_a > 0.55:
        st.write("✔ Favorito: Time A")

    elif prob_b > 0.55:
        st.write("✔ Favorito: Time B")

    else:
        st.write("⚠️ Jogo equilibrado")
