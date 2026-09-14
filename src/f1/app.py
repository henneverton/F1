"""Dashboard Streamlit: top 5 voltas mais rápidas por pista e sessão."""

from __future__ import annotations

import altair as alt
import pandas as pd
import streamlit as st

from f1.models import RankedLap
from f1.openf1_client import OpenF1Client, OpenF1Error
from f1.ranking import rank_fastest_laps

MIN_YEAR = 2023
CURRENT_YEAR = 2026


@st.cache_resource
def get_client() -> OpenF1Client:
    return OpenF1Client()


@st.cache_data(ttl="15m")
def load_meetings(year: int):
    return get_client().get_meetings(year)


@st.cache_data(ttl="15m")
def load_sessions(meeting_key: int):
    return get_client().get_sessions(meeting_key)


@st.cache_data(ttl="5m")
def load_drivers(session_key: int):
    return get_client().get_drivers(session_key)


@st.cache_data(ttl="5m")
def load_laps(session_key: int):
    return get_client().get_laps(session_key)


def _format_sector(value: float | None) -> str:
    return f"{value:.3f}" if value is not None else "-"


def ranked_laps_to_dataframe(ranked: list[RankedLap]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "position": [item.position for item in ranked],
            "label": [f"P{item.position} · {item.driver_name}" for item in ranked],
            "driver_name": [item.driver_name for item in ranked],
            "team_name": [item.team_name for item in ranked],
            "driver_number": [item.driver_number for item in ranked],
            "lap_number": [item.lap_number for item in ranked],
            "lap_duration": [item.lap_duration for item in ranked],
            "lap_duration_formatted": [item.lap_duration_formatted for item in ranked],
            "sector_1": [_format_sector(item.duration_sector_1) for item in ranked],
            "sector_2": [_format_sector(item.duration_sector_2) for item in ranked],
            "sector_3": [_format_sector(item.duration_sector_3) for item in ranked],
        }
    )


def default_session_index(sessions: list) -> int:
    for index, session in enumerate(sessions):
        if session.session_type.lower() == "race":
            return index
    return 0


st.set_page_config(
    page_title="F1 — Top 5 voltas mais rápidas",
    page_icon=":material/timer:",
    layout="wide",
)

st.title("Top 5 voltas mais rápidas")
st.caption(
    "Dados históricos da OpenF1 API (gratuitos desde 2023, sem necessidade de autenticação)."
)

with st.sidebar:
    st.header("Filtros")
    year = st.selectbox("Época", options=list(range(CURRENT_YEAR, MIN_YEAR - 1, -1)))

try:
    meetings = load_meetings(year)
except OpenF1Error as exc:
    st.error(f"Não foi possível carregar as pistas: {exc}")
    st.stop()

if not meetings:
    st.info("Não há Grandes Prémios registados para esta época.")
    st.stop()

meetings_by_label = {f"{m.meeting_name} — {m.country_name}": m for m in meetings}

with st.sidebar:
    meeting_label = st.selectbox("Pista / Grande Prémio", options=list(meetings_by_label))

selected_meeting = meetings_by_label[meeting_label]

try:
    sessions = load_sessions(selected_meeting.meeting_key)
except OpenF1Error as exc:
    st.error(f"Não foi possível carregar as sessões: {exc}")
    st.stop()

if not sessions:
    st.info("Não há sessões registadas para esta pista.")
    st.stop()

session_labels = [s.session_name for s in sessions]
sessions_by_label = dict(zip(session_labels, sessions, strict=True))

with st.sidebar:
    session_label = st.selectbox(
        "Sessão",
        options=session_labels,
        index=default_session_index(sessions),
    )

selected_session = sessions_by_label[session_label]

st.subheader(f"{selected_meeting.meeting_name} — {selected_session.session_name}")
if selected_session.date_start:
    st.caption(f"Início: {selected_session.date_start}")

try:
    drivers = load_drivers(selected_session.session_key)
    laps = load_laps(selected_session.session_key)
except OpenF1Error as exc:
    st.error(f"Não foi possível carregar os dados de volta: {exc}")
    st.stop()

ranked = rank_fastest_laps(laps, drivers)

if not ranked:
    st.warning("Nenhuma volta válida encontrada para esta sessão. Tente outra sessão ou pista.")
    st.stop()

df = ranked_laps_to_dataframe(ranked)

with st.container(border=True):
    st.markdown("**Top 5 voltas mais rápidas**")
    st.dataframe(
        df,
        hide_index=True,
        column_config={
            "position": st.column_config.NumberColumn("Pos."),
            "label": None,
            "driver_name": st.column_config.TextColumn("Piloto"),
            "team_name": st.column_config.TextColumn("Equipa"),
            "driver_number": st.column_config.NumberColumn("Número"),
            "lap_number": st.column_config.NumberColumn("Volta"),
            "lap_duration": None,
            "lap_duration_formatted": st.column_config.TextColumn("Tempo"),
            "sector_1": st.column_config.TextColumn("Setor 1"),
            "sector_2": st.column_config.TextColumn("Setor 2"),
            "sector_3": st.column_config.TextColumn("Setor 3"),
        },
    )

with st.container(border=True):
    st.markdown("**Comparação visual**")
    min_time = df["lap_duration"].min()
    max_time = df["lap_duration"].max()
    padding = max((max_time - min_time) * 0.5, 0.05)
    chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            y=alt.Y("label:N", sort=df["label"].tolist(), title=None),
            x=alt.X(
                "lap_duration:Q",
                title="Tempo de volta (s)",
                scale=alt.Scale(domain=[max(min_time - padding, 0), max_time + padding]),
            ),
            tooltip=[
                alt.Tooltip("driver_name:N", title="Piloto"),
                alt.Tooltip("team_name:N", title="Equipa"),
                alt.Tooltip("lap_duration_formatted:N", title="Tempo"),
            ],
        )
    )
    st.altair_chart(chart)
