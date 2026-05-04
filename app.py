import streamlit as st
import random
import math

st.title("⚽ Robô Inteligente 2.0 (Brasileirão)")

# FORÇA DOS TIMES (base realista aproximada)
times = {
    "Flamengo": 88,
    "Palmeiras": 89,
    "São Paulo": 80,
    "Corinthians": 78,
    "Vasco": 75,
    "Fluminense": 82,
    "Botafogo": 83,
    "Grêmio": 81,
    "Internacional": 82,
    "Atlético-MG": 85,
    "Cruzeiro": 79,
    "Bahia": 78,
    "Fortaleza": 80,
    "Ceará": 74,
    "Sport": 72,
    "Vitória": 73,
    "Bragantino": 81,
    "Athletico-PR": 82,
    "Goiás": 71,
    "Juventude": 70
}

def expectativa_gols(forca_a, forca_b, casa=True):
    """Modelo simples tipo Poisson reduzido"""
    
    vantagem_casa = 1.15 if casa else 1.0
    
    ataque_a = forca_a * vantagem_casa
    defesa_b = forca_b
    
    ataque_b = forca_b * (1.0 if casa else 1.15)
    defesa_a = forca_a
    
    lambda_a = max(0.2, (ataque_a - defesa_b) / 30)
    lambda_b = max(0.2, (ataque_b - defesa_a) / 30)

    gols_a = min(5, int(random.gauss(lambda_a, 1)))
    gols_b = min(5, int(random.gauss(lambda_b, 1)))

    return max(0, gols_a), max(0, gols_b)

def calcular_probabilidades(gols_a, gols_b):
    if gols_a > gols_b:
        return 55, 20, 25
    elif gols_b > gols_a:
        return 25, 20, 55
    else:
        return 35, 30, 35


# UI
time_a = st.selectbox("Time A (Casa)", list(times.keys()))
time_b = st.selectbox("Time B (Visitante)", list(times.keys()))

if st.button("Simular Jogo"):

    if time_a == time_b:
        st.warning("Escolha times diferentes!")
        st.stop()

    forca_a = times[time_a]
    forca_b = times[time_b]

    gols_a, gols_b = expectativa_gols(forca_a, forca_b, casa=True)

    prob_a, empate, prob_b = calcular_probabilidades(gols_a, gols_b)

    st.subheader("📊 Probabilidades")

    st.success(f"{time_a}: {prob_a:.1f}%")
    st.info(f"Empate: {empate:.1f}%")
    st.success(f"{time_b}: {prob_b:.1f}%")

    st.subheader("🎯 Placar provável")
    st.write(f"{time_a} {gols_a} x {gols_b} {time_b}")

    # leitura extra estilo “robô”
    if gols_a > gols_b:
        st.write(f"🔮 Leitura: vitória do {time_a} com vantagem leve.")
    elif gols_b > gols_a:
        st.write(f"🔮 Leitura: {time_b} deve surpreender fora de casa.")
    else:
        st.write("🔮 Leitura: jogo equilibrado, tendência forte de empate.")
