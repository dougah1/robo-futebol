import streamlit as st
import random

st.title("⚽ Robô Inteligente (Sem API)")

# Times com força base (você pode expandir depois)
times = {
    "Flamengo": 85,
    "Palmeiras": 88,
    "São Paulo": 78,
    "Corinthians": 76,
    "Remo": 65
}

def simular_jogo(forca_a, forca_b):
    # Simula forma recente
    forma_a = random.randint(-5, 5)
    forma_b = random.randint(-5, 5)

    ataque_a = forca_a + forma_a
    ataque_b = forca_b + forma_b

    defesa_a = forca_a - random.randint(0, 10)
    defesa_b = forca_b - random.randint(0, 10)

    score_a = ataque_a - defesa_b
    score_b = ataque_b - defesa_a

    total = abs(score_a) + abs(score_b)

    if total == 0:
        return 33, 34, 33

    prob_a = (abs(score_a) / total) * 100
    prob_b = (abs(score_b) / total) * 100
    empate = 100 - (prob_a + prob_b)

    return prob_a, empate, prob_b


time_a = st.selectbox("Time A", list(times.keys()))
time_b = st.selectbox("Time B", list(times.keys()))

if st.button("Analisar"):

    forca_a = times[time_a]
    forca_b = times[time_b]

    prob_a, empate, prob_b = simular_jogo(forca_a, forca_b)

    st.subheader("📊 Probabilidades")

    st.success(f"{time_a}: {prob_a:.1f}%")
    st.info(f"Empate: {empate:.1f}%")
    st.success(f"{time_b}: {prob_b:.1f}%")

    # Previsão de placar
    gols_a = max(0, int(prob_a // 20))
    gols_b = max(0, int(prob_b // 20))

    st.subheader("🎯 Placar provável")
    st.write(f"{time_a} {gols_a} x {gols_b} {time_b}")
