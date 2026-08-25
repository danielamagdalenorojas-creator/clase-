El problema ya no está en main.py. Streamlit sigue sin encontrar Matplotlib porque probablemente el segundo archivo está mal escrito.

Debe llamarse exactamente:

requirements.txt

No:

requirments.txt

Fíjate que lleva “require” completo.

En GitHub abre el archivo, presiona el lápiz ✏️ y cambia el nombre a:

requirements.txt

Su contenido debe ser únicamente:

streamlit
pandas
matplotlib
statsbombpy
mplsoccer

Guarda con Commit changes y verifica que en la página principal aparezcan exactamente:

main.py
requirements.txt

Después entra a Streamlit y pulsa:

Manage app → Reboot app

Si el archivo ya tiene ese nombre exacto, necesito una captura de la página de GitHub donde se vean ambos archivos; la captura del error no permite comprobar el nombre ni la ubicación de requirements.txt.

¡Ya encontré el problema! El archivo está escrito como:

requirments.txt

Debe llamarse:

requirements.txt

Te falta una “e” después de r.

Para corregirlo:

Abre requirments.txt.
Presiona el lápiz ✏️.
Cambia el nombre de arriba por requirements.txt.
Confirma que contenga:
streamlit
pandas
matplotlib
statsbombpy
mplsoccer
Pulsa Commit changes.
En Streamlit selecciona Manage app → Reboot app.

Con eso Streamlit ya podrá detectar el archivo e instalar Matplotlib.

puedes hacer una app increible con todo lo basico que se ocupa y que este optimizado el codigo

Sí. Ya preparé una versión completa, visual y optimizada de tu app de fútbol.

Incluye:

Todos los partidos del Mundial 2022.
Filtros por partido, equipo, minutos, jugador y resultado.
Mapa de pases interactivo.
Precisión, pases progresivos y longitud promedio.
Comparativa de jugadores.
Mapa de tiros con xG y goles.
Descarga de datos en CSV.
Caché para evitar descargas repetidas.
Diseño oscuro adaptable a móvil y computadora.
Manejo de errores.

Descarga el proyecto completo:

Descargar futbol_lab_streamlit.zip

También puedes descargar los archivos individualmente:

main.py
requirements.txt
README.md

Descomprime el ZIP y reemplaza en GitHub tu main.py y requirements.txt. Después haz Commit changes y selecciona Manage app → Reboot app en Streamlit.

main.py
Code
requirements.txt
Document
README.md
Document

Library
/
main.py
from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from mplsoccer import Pitch, VerticalPitch
from statsbombpy import sb


# -----------------------------------------------------------------------------
# Configuración general
# -----------------------------------------------------------------------------
COMPETITION_ID = 43
SEASON_ID = 106
PITCH_COLOR = "#0B1324"
LINE_COLOR = "#D8E4F0"
SUCCESS_COLOR = "#24D3A6"
FAIL_COLOR = "#FF6B7A"
ACCENT_COLOR = "#47A7FF"

st.set_page_config(
    page_title="Fútbol Lab | Qatar 2022",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .stApp {
            background:
                radial-gradient(circle at 85% 0%, rgba(71,167,255,.12), transparent 28rem),
                linear-gradient(180deg, #07101f 0%, #0b1424 100%);
        }
        .block-container {max-width: 1450px; padding-top: 1.5rem;}
        [data-testid="stSidebar"] {background: #08111f; border-right: 1px solid #1d2c40;}
        [data-testid="stMetric"] {
            background: linear-gradient(145deg, #111d30, #0d1727);
            border: 1px solid #20324b;
            border-radius: 16px;
            padding: 1rem 1.1rem;
            box-shadow: 0 10px 30px rgba(0,0,0,.16);
        }
        [data-testid="stMetricLabel"] {color: #9eb1c8;}
        [data-testid="stMetricValue"] {color: #f5f9ff;}
        .hero {
            background: linear-gradient(125deg, rgba(36,211,166,.15), rgba(71,167,255,.12));
            border: 1px solid #24405b;
            border-radius: 22px;
            padding: 1.35rem 1.55rem;
            margin-bottom: 1rem;
        }
        .hero-kicker {color: #74e9cd; font-size: .82rem; font-weight: 700; letter-spacing: .12em;}
        .hero-title {color: #f7fbff; font-size: clamp(1.65rem, 3vw, 2.7rem); font-weight: 800; margin: .25rem 0;}
        .hero-meta {color: #a8b8ca; font-size: .95rem;}
        .section-note {color: #8fa4bb; font-size: .9rem;}
        div[data-testid="stDataFrame"] {border: 1px solid #20324b; border-radius: 14px; overflow: hidden;}
        .stTabs [data-baseweb="tab-list"] {gap: .45rem;}
        .stTabs [data-baseweb="tab"] {background: #0e1929; border-radius: 10px; padding: .55rem 1rem;}
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------------------------------------------------------
# Carga y preparación de datos
# -----------------------------------------------------------------------------
@st.cache_data(ttl=86_400, show_spinner=False)
def load_matches() -> pd.DataFrame:
    """Descarga una vez el catálogo de partidos del Mundial 2022."""
    matches = sb.matches(competition_id=COMPETITION_ID, season_id=SEASON_ID)
    matches = matches.sort_values(["match_date", "kick_off"], ascending=False).reset_index(drop=True)
    matches["match_label"] = (
        matches["home_team"]
        + "  vs  "
        + matches["away_team"]
        + " · "
        + matches["match_date"].astype(str)
    )
    return matches


def _coordinates(series: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Convierte listas [x, y] en dos arreglos numéricos."""
    values = np.stack(series.to_numpy())
    return values[:, 0].astype(float), values[:, 1].astype(float)


@st.cache_data(ttl=86_400, show_spinner=False)
def load_match_data(match_id: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Descarga y transforma pases y tiros; el resultado queda en caché."""
    events = sb.events(match_id=match_id)

    passes = events.loc[events["type"].eq("Pass")].copy()
    passes = passes.dropna(subset=["location", "pass_end_location"])

    passes["x"], passes["y"] = _coordinates(passes["location"])
    passes["end_x"], passes["end_y"] = _coordinates(passes["pass_end_location"])

    if "pass_outcome" not in passes:
        passes["pass_outcome"] = pd.NA
    if "pass_length" not in passes:
        passes["pass_length"] = np.hypot(
            passes["end_x"] - passes["x"], passes["end_y"] - passes["y"]
        )

    passes["completed"] = passes["pass_outcome"].isna()
    start_goal_distance = np.hypot(120 - passes["x"], 40 - passes["y"])
    end_goal_distance = np.hypot(120 - passes["end_x"], 40 - passes["end_y"])
    passes["progressive"] = (start_goal_distance - end_goal_distance) >= (
        start_goal_distance * 0.25
    )

    shots = events.loc[events["type"].eq("Shot")].copy()
    shots = shots.dropna(subset=["location"])
    if not shots.empty:
        shots["x"], shots["y"] = _coordinates(shots["location"])
    if "shot_statsbomb_xg" not in shots:
        shots["shot_statsbomb_xg"] = 0.0
    if "shot_outcome" not in shots:
        shots["shot_outcome"] = "Desconocido"

    return passes, shots


def safe_text(value: object, fallback: str = "—") -> str:
    return fallback if pd.isna(value) or value == "" else str(value)


def filter_passes(
    passes: pd.DataFrame,
    team: str,
    minute_range: tuple[int, int],
    player: str,
    result: str,
) -> pd.DataFrame:
    """Aplica todos los filtros de la interfaz en un único paso."""
    start, end = minute_range
    mask = passes["team"].eq(team) & passes["minute"].between(start, end)

    if player != "Todos":
        mask &= passes["player"].eq(player)
    if result == "Completos":
        mask &= passes["completed"]
    elif result == "Incompletos":
        mask &= ~passes["completed"]

    return passes.loc[mask].copy()


def draw_pass_map(data: pd.DataFrame, team: str, show_origins: bool) -> plt.Figure:
    pitch = Pitch(
        pitch_type="statsbomb",
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.25,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(13, 8))
    fig.set_facecolor(PITCH_COLOR)

    completed = data.loc[data["completed"]]
    incomplete = data.loc[~data["completed"]]

    if not completed.empty:
        pitch.arrows(
            completed["x"], completed["y"], completed["end_x"], completed["end_y"],
            ax=ax, color=SUCCESS_COLOR, width=1.15, headwidth=3.3, headlength=4.2,
            alpha=0.72, zorder=2,
        )
    if not incomplete.empty:
        pitch.arrows(
            incomplete["x"], incomplete["y"], incomplete["end_x"], incomplete["end_y"],
            ax=ax, color=FAIL_COLOR, width=1.05, headwidth=3.2, headlength=4.0,
            alpha=0.65, zorder=2,
        )
    if show_origins and not data.empty:
        origin_colors = np.where(data["completed"], SUCCESS_COLOR, FAIL_COLOR)
        pitch.scatter(
            data["x"], data["y"], ax=ax, s=15, c=origin_colors,
            edgecolors=PITCH_COLOR, linewidth=.25, alpha=.9, zorder=3,
        )

    legend = [
        Line2D([0], [0], color=SUCCESS_COLOR, lw=3, label="Completo"),
        Line2D([0], [0], color=FAIL_COLOR, lw=3, label="Incompleto"),
    ]
    ax.legend(
        handles=legend, loc="upper left", frameon=True, facecolor="#101d30",
        edgecolor="#2b405b", labelcolor="white", fontsize=10,
    )
    ax.set_title(
        f"Mapa de pases · {team}", color="white", fontsize=18,
        fontweight="bold", pad=14,
    )
    return fig


def draw_shot_map(shots: pd.DataFrame, team: str) -> plt.Figure:
    pitch = VerticalPitch(
        pitch_type="statsbomb",
        half=True,
        pitch_color=PITCH_COLOR,
        line_color=LINE_COLOR,
        linewidth=1.25,
        corner_arcs=True,
    )
    fig, ax = pitch.draw(figsize=(8, 8))
    fig.set_facecolor(PITCH_COLOR)

    if not shots.empty:
        xg = pd.to_numeric(shots["shot_statsbomb_xg"], errors="coerce").fillna(0)
        goals = shots["shot_outcome"].eq("Goal")
        sizes = 90 + xg * 1_350

        pitch.scatter(
            shots.loc[~goals, "x"], shots.loc[~goals, "y"],
            s=sizes.loc[~goals], ax=ax, color=ACCENT_COLOR,
            edgecolors="white", linewidth=.7, alpha=.72, zorder=3,
        )
        pitch.scatter(
            shots.loc[goals, "x"], shots.loc[goals, "y"],
            s=sizes.loc[goals] + 90, ax=ax, color="#FFD166", marker="*",
            edgecolors="white", linewidth=.9, alpha=.95, zorder=4,
        )

    ax.set_title(
        f"Mapa de tiros · {team}", color="white", fontsize=18,
        fontweight="bold", pad=14,
    )
    return fig


# -----------------------------------------------------------------------------
# Aplicación
# -----------------------------------------------------------------------------
try:
    matches = load_matches()
except Exception as error:
    st.error("No fue posible descargar el catálogo de partidos. Intenta reiniciar la app.")
    with st.expander("Detalle técnico"):
        st.exception(error)
    st.stop()

with st.sidebar:
    st.markdown("## ⚙️ Panel de control")
    st.caption("Cambia los filtros y el análisis se actualizará automáticamente.")
    match_label = st.selectbox("Partido", matches["match_label"].tolist())

match = matches.loc[matches["match_label"].eq(match_label)].iloc[0]
match_id = int(match["match_id"])

try:
    with st.spinner("Preparando los datos del partido..."):
        passes, shots = load_match_data(match_id)
except Exception as error:
    st.error("No fue posible descargar los eventos de este partido.")
    with st.expander("Detalle técnico"):
        st.exception(error)
    st.stop()

teams = [match["home_team"], match["away_team"]]
max_minute = int(max(passes["minute"].max(), shots["minute"].max() if not shots.empty else 90))

with st.sidebar:
    team = st.radio("Equipo", teams, horizontal=True)
    minute_range = st.slider(
        "Rango de minutos", 0, max_minute, (0, min(90, max_minute)),
    )
    available_players = sorted(
        passes.loc[passes["team"].eq(team), "player"].dropna().unique().tolist()
    )
    player = st.selectbox("Jugador", ["Todos", *available_players])
    result = st.radio("Resultado del pase", ["Todos", "Completos", "Incompletos"])
    show_origins = st.toggle("Mostrar puntos de origen", value=True)
    st.divider()
    st.caption("Fuente: StatsBomb Open Data · FIFA World Cup 2022")

filtered = filter_passes(passes, team, minute_range, player, result)
team_period_passes = filter_passes(passes, team, minute_range, "Todos", "Todos")
team_shots = shots.loc[
    shots["team"].eq(team) & shots["minute"].between(*minute_range)
].copy()

home_score = safe_text(match.get("home_score", 0), "0")
away_score = safe_text(match.get("away_score", 0), "0")
stage = safe_text(match.get("competition_stage"), "FIFA World Cup 2022")
stadium = safe_text(match.get("stadium"))

st.markdown(
    f"""
    <div class="hero">
        <div class="hero-kicker">FÚTBOL LAB · QATAR 2022</div>
        <div class="hero-title">{match['home_team']} {home_score} — {away_score} {match['away_team']}</div>
        <div class="hero-meta">{stage} · {match['match_date']} · {stadium}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

total = len(filtered)
complete = int(filtered["completed"].sum()) if total else 0
accuracy = complete / total * 100 if total else 0.0
progressive = int(filtered["progressive"].sum()) if total else 0
average_length = float(filtered["pass_length"].mean()) if total else 0.0

metric_cols = st.columns(5)
metric_cols[0].metric("Pases", f"{total:,}")
metric_cols[1].metric("Completos", f"{complete:,}")
metric_cols[2].metric("Precisión", f"{accuracy:.1f}%")
metric_cols[3].metric("Progresivos", f"{progressive:,}")
metric_cols[4].metric("Longitud media", f"{average_length:.1f} m")

map_tab, players_tab, shots_tab, data_tab = st.tabs(
    ["🗺️ Mapa de pases", "👟 Jugadores", "🎯 Tiros", "📋 Datos"]
)

with map_tab:
    if filtered.empty:
        st.info("No hay pases que coincidan con los filtros actuales.")
    else:
        pass_figure = draw_pass_map(filtered, team, show_origins)
        st.pyplot(pass_figure, use_container_width=True)
        plt.close(pass_figure)
    st.markdown(
        '<p class="section-note">Las flechas verdes son pases completos; las rosas son incompletos.</p>',
        unsafe_allow_html=True,
    )

with players_tab:
    if team_period_passes.empty:
        st.info("No hay información de jugadores para este rango.")
    else:
        player_table = (
            team_period_passes.dropna(subset=["player"])
            .groupby("player", as_index=False)
            .agg(
                Pases=("completed", "size"),
                Completos=("completed", "sum"),
                Progresivos=("progressive", "sum"),
                Longitud_media=("pass_length", "mean"),
            )
        )
        player_table["Precisión"] = (
            player_table["Completos"] / player_table["Pases"] * 100
        )
        player_table = player_table.sort_values(
            ["Pases", "Precisión"], ascending=False
        ).rename(
            columns={"player": "Jugador", "Longitud_media": "Longitud media", "Precisión": "Precisión (%)"}
        )
        player_table["Longitud media"] = player_table["Longitud media"].round(1)
        player_table["Precisión (%)"] = player_table["Precisión (%)"].round(1)

        st.subheader(f"Rendimiento de pase · {team}")
        st.dataframe(player_table, hide_index=True, use_container_width=True)

with shots_tab:
    shot_col, shot_metrics_col = st.columns([1.55, 1])
    with shot_col:
        shot_figure = draw_shot_map(team_shots, team)
        st.pyplot(shot_figure, use_container_width=True)
        plt.close(shot_figure)
    with shot_metrics_col:
        goals = int(team_shots["shot_outcome"].eq("Goal").sum()) if not team_shots.empty else 0
        total_xg = pd.to_numeric(
            team_shots.get("shot_statsbomb_xg", pd.Series(dtype=float)), errors="coerce"
        ).fillna(0).sum()
        st.subheader("Resumen ofensivo")
        st.metric("Tiros", len(team_shots))
        st.metric("Goles", goals)
        st.metric("xG acumulado", f"{total_xg:.2f}")
        st.caption("El tamaño del círculo representa el xG. Las estrellas amarillas son goles.")

with data_tab:
    export_columns = [
        "minute", "second", "team", "player", "pass_recipient", "pass_length",
        "pass_height", "pass_body_part", "pass_outcome", "x", "y", "end_x", "end_y",
    ]
    existing_columns = [column for column in export_columns if column in filtered.columns]
    export = filtered[existing_columns].copy()
    export = export.rename(
        columns={
            "minute": "Minuto", "second": "Segundo", "team": "Equipo",
            "player": "Jugador", "pass_recipient": "Receptor",
            "pass_length": "Longitud", "pass_height": "Altura",
            "pass_body_part": "Parte del cuerpo", "pass_outcome": "Resultado",
            "end_x": "X final", "end_y": "Y final",
        }
    )
    st.dataframe(export, hide_index=True, use_container_width=True)
    st.download_button(
        "⬇️ Descargar pases filtrados (CSV)",
        data=export.to_csv(index=False).encode("utf-8-sig"),
        file_name=f"pases_{team.replace(' ', '_')}_{minute_range[0]}-{minute_range[1]}.csv",
        mime="text/csv",
        use_container_width=True,
    )

st.caption(
    "Pase progresivo: reduce al menos 25% de la distancia restante hacia la portería rival. "
    "Datos abiertos proporcionados por StatsBomb."
)
