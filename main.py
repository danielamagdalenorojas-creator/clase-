import streamlit as st

st.title("Análisis de pases de fútbol")

minuto = st.slider(
    "Selecciona el minuto:",
    min_value=0,
    max_value=90,
    value=45
)

st.write("Minuto seleccionado:", minuto)
