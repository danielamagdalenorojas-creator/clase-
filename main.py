import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from statsbombpy import sb
from mplsoccer import Pitch

st.set_page_config(
    page_title="Mapa de pases",
    page_icon="⚽",
    layout="wide"
)

st.title("⚽ Mapa interactivo de pases")
st.write("Partidos del Mundial de Qatar 2022")


@st.cache_data(show_spinner="Descargando partidos...")
def cargar_partidos():
    return sb.matches(
        competition_id=43,
        season_id=106
    ).reset_index(drop=True)


@st.cache_data(show_spinner="Descargando eventos...")
def cargar_eventos(match_id):
    return sb.events(match_id=match_id)


# Descargar partidos
matches = cargar_partidos()

# Crear el nombre que aparecerá en el selector
matches["nombre_partido"] = (
    matches["home_team"]
    + " vs "
    + matches["away_team"]
    + " — "
    + matches["match_date"].astype(str)
)

# Selector de partido
partido_seleccionado = st.selectbox(
    "Selecciona un partido:",
    matches["nombre_partido"].tolist()
)

# Encontrar el partido seleccionado
partido = matches[
    matches["nombre_partido"] == partido_seleccionado
].iloc[0]

match_id = int(partido["match_id"])

# Descargar los eventos
events = cargar_eventos(match_id)

# Filtrar solamente los pases
passes = events[
    events["type"] == "Pass"
].copy()

# Eliminar pases sin coordenadas
passes = passes.dropna(
    subset=["location", "pass_end_location"]
)

# Separar coordenadas iniciales
passes[["x", "y"]] = pd.DataFrame(
    passes["location"].tolist(),
    index=passes.index
)

# Separar coordenadas finales
passes[["end_x", "end_y"]] = pd.DataFrame(
    passes["pass_end_location"].tolist(),
    index=passes.index
)

# Crear la columna si no aparece en los datos
if "pass_outcome" not in passes.columns:
    passes["pass_outcome"] = pd.NA

# Selector de equipo
equipo = st.selectbox(
    "Selecciona un equipo:",
    sorted(passes["team"].dropna().unique())
)

# Selector de minuto
minuto = st.slider(
    "Selecciona el minuto:",
    min_value=0,
    max_value=int(passes["minute"].max()),
    value=45
)

# Filtrar pases acumulados hasta el minuto seleccionado
datos = passes[
    (passes["minute"] <= minuto)
    & (passes["team"] == equipo)
]

# Separar pases completos e incompletos
completos = datos[
    datos["pass_outcome"].isna()
]

incompletos = datos[
    datos["pass_outcome"].notna()
]

# Crear la cancha
pitch = Pitch(
    pitch_type="statsbomb",
    pitch_color="#176B3A",
    line_color="white",
    linewidth=2
)

fig, ax = pitch.draw(
    figsize=(12, 8)
)

# Dibujar pases completos
pitch.arrows(
    completos["x"],
    completos["y"],
    completos["end_x"],
    completos["end_y"],
    color="#FFD700",
    width=1.5,
    headwidth=4,
    alpha=0.65,
    ax=ax,
    label="Pase completo"
)

# Dibujar pases incompletos
pitch.arrows(
    incompletos["x"],
    incompletos["y"],
    incompletos["end_x"],
    incompletos["end_y"],
    color="#FF4B4B",
    width=1.5,
    headwidth=4,
    alpha=0.65,
    ax=ax,
    label="Pase incompleto"
)

ax.set_title(
    f"{equipo}: pases hasta el minuto {minuto}",
    fontsize=18,
    fontweight="bold",
    color="white",
    pad=15
)

ax.legend(
    loc="upper left",
    facecolor="white"
)

# Mostrar el mapa
st.pyplot(fig)

# Mostrar estadísticas
columna1, columna2, columna3 = st.columns(3)

columna1.metric(
    "Pases totales",
    len(datos)
)

columna2.metric(
    "Pases completos",
    len(completos)
)

columna3.metric(
    "Pases incompletos",
    len(incompletos)
)
