"""Dashboard Streamlit: top 5 voltas mais rápidas por pista e sessão."""

from __future__ import annotations

from dataclasses import dataclass, field

import altair as alt
import pandas as pd
import streamlit as st

from f1.geo import build_calendar_map
from f1.models import Driver, Meeting, RankedLap, Session, SessionResult
from f1.openf1_client import OpenF1Client, OpenF1Error
from f1.ranking import rank_fastest_laps, tally_wins
from f1.theme import CUSTOM_CSS, SIDEBAR_CAR_SVG

MIN_YEAR = 2023
CURRENT_YEAR = 2026
ALL_COUNTRIES_OPTION = "Todos os países"
SESSION_TYPES: list[tuple[str, str]] = [
    ("Race", "Corrida"),
    ("Qualifying", "Qualificação"),
    ("Practice", "Treino Livre"),
]
SESSION_TYPE_LABELS = dict(SESSION_TYPES)

LAPS_COLUMN_CONFIG = {
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
}


@dataclass
class TrackData:
    """Dados de uma pista já carregados para a sessão/tipo escolhidos."""

    meeting: Meeting
    session: Session | None = None
    drivers: list[Driver] = field(default_factory=list)
    session_results: list[SessionResult] = field(default_factory=list)
    ranked_laps: list[RankedLap] = field(default_factory=list)
    error: str | None = None


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


@st.cache_data(ttl="5m")
def load_session_results(session_key: int):
    return get_client().get_session_results(session_key)


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


def meetings_to_dataframe(meetings: list[Meeting]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "meeting_name": [m.meeting_name for m in meetings],
            "circuit_short_name": [m.circuit_short_name for m in meetings],
            "country_name": [m.country_name for m in meetings],
            "date": [m.date_start.split("T")[0] if m.date_start else "-" for m in meetings],
        }
    )


def find_session_by_type(sessions: list[Session], session_type: str) -> Session | None:
    """Devolve a sessão mais recente do tipo indicado, ou `None` se não existir."""

    matches = [s for s in sessions if s.session_type.lower() == session_type.lower()]
    if not matches:
        return None
    return max(matches, key=lambda s: s.date_start or "")


def load_track_data(meeting: Meeting, session_type: str) -> TrackData:
    """Carrega sessão, pilotos, classificação e voltas de uma pista, sem levantar exceções."""

    try:
        sessions = load_sessions(meeting.meeting_key)
    except OpenF1Error as exc:
        return TrackData(meeting=meeting, error=str(exc))

    session = find_session_by_type(sessions, session_type)
    if session is None:
        return TrackData(meeting=meeting)

    try:
        drivers = load_drivers(session.session_key)
        laps = load_laps(session.session_key)
        session_results = load_session_results(session.session_key)
    except OpenF1Error as exc:
        return TrackData(meeting=meeting, session=session, error=str(exc))

    return TrackData(
        meeting=meeting,
        session=session,
        drivers=drivers,
        session_results=session_results,
        ranked_laps=rank_fastest_laps(laps, drivers),
    )


def top_drivers_to_dataframe(top_drivers) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "driver_name": [d.driver_name for d in top_drivers],
            "team_name": [d.team_name for d in top_drivers],
            "wins": [d.wins for d in top_drivers],
        }
    )


st.set_page_config(
    page_title="F1 — Top 5 voltas mais rápidas",
    page_icon=":material/timer:",
    layout="wide",
)

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

st.title("Top 5 voltas mais rápidas")
st.caption(
    "Dados históricos da OpenF1 API (gratuitos desde 2023, sem necessidade de autenticação)."
)

with st.sidebar:
    st.markdown(SIDEBAR_CAR_SVG, unsafe_allow_html=True)
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

countries = sorted({m.country_name for m in meetings if m.country_name})

with st.sidebar:
    country_filter = st.selectbox("País", options=[ALL_COUNTRIES_OPTION, *countries])
    session_type = st.selectbox(
        "Tipo de sessão",
        options=[key for key, _ in SESSION_TYPES],
        format_func=lambda key: SESSION_TYPE_LABELS[key],
    )

filtered_meetings = (
    meetings
    if country_filter == ALL_COUNTRIES_OPTION
    else [m for m in meetings if m.country_name == country_filter]
)
filtered_meetings = sorted(filtered_meetings, key=lambda m: m.date_start or "")

if not filtered_meetings:
    st.info("Não há Grandes Prémios registados para este país nesta época.")
    st.stop()

with st.spinner("A carregar dados de todas as pistas…"):
    tracks_data = [load_track_data(meeting, session_type) for meeting in filtered_meetings]

with st.container(border=True, key="map_card"):
    st.markdown("**Mapa do calendário**")
    highlighted_country = country_filter if country_filter != ALL_COUNTRIES_OPTION else None
    st.altair_chart(
        build_calendar_map([m.country_name for m in meetings], highlighted_country),
        width="stretch",
    )

with st.container(border=True, key="top_drivers_card"):
    st.markdown("**Top 3 pilotos**")
    scope_label = country_filter if country_filter != ALL_COUNTRIES_OPTION else "todos os países"
    st.caption(f"{SESSION_TYPE_LABELS[session_type]} · {scope_label} · Época {year}")

    top_drivers = tally_wins(
        [(t.session_results, t.drivers) for t in tracks_data if t.session is not None]
    )

    if not top_drivers:
        st.info("Sem vitórias registadas para os filtros selecionados.")
    else:
        top_drivers_df = top_drivers_to_dataframe(top_drivers)
        chart = (
            alt.Chart(top_drivers_df)
            .mark_bar(cornerRadiusEnd=6)
            .encode(
                y=alt.Y("driver_name:N", sort="-x", title=None),
                x=alt.X("wins:Q", title="Vitórias", axis=alt.Axis(tickMinStep=1)),
                color=alt.Color(
                    "driver_name:N",
                    legend=None,
                    scale=alt.Scale(range=["#ff8fa3", "#ffc785", "#7fd1ff"]),
                ),
                tooltip=[
                    alt.Tooltip("driver_name:N", title="Piloto"),
                    alt.Tooltip("team_name:N", title="Equipa"),
                    alt.Tooltip("wins:Q", title="Vitórias"),
                ],
            )
        )
        labels = (
            alt.Chart(top_drivers_df)
            .mark_text(align="left", dx=6, fontWeight="bold")
            .encode(
                y=alt.Y("driver_name:N", sort="-x"),
                x=alt.X("wins:Q"),
                text=alt.Text("wins:Q"),
            )
        )
        st.altair_chart(chart + labels, width="stretch")

with st.container(border=True, key="tracks_card"):
    st.markdown("**Pistas da época**")
    st.dataframe(
        meetings_to_dataframe(filtered_meetings),
        hide_index=True,
        column_config={
            "meeting_name": st.column_config.TextColumn("Grande Prémio"),
            "circuit_short_name": st.column_config.TextColumn("Circuito"),
            "country_name": st.column_config.TextColumn("País"),
            "date": st.column_config.TextColumn("Data"),
        },
    )

st.subheader(f"5 melhores voltas por pista — {SESSION_TYPE_LABELS[session_type]}")

for track in tracks_data:
    with st.container(border=True, key=f"laps_card_{track.meeting.meeting_key}"):
        st.markdown(f"**{track.meeting.meeting_name} — {track.meeting.country_name}**")

        if track.error:
            st.error(f"Não foi possível carregar os dados desta pista: {track.error}")
            continue

        if track.session is None:
            st.info(
                f"Sem sessão de {SESSION_TYPE_LABELS[session_type].lower()} "
                "registada para esta pista."
            )
            continue

        if track.session.date_start:
            st.caption(f"{track.session.session_name} · Início: {track.session.date_start}")

        if not track.ranked_laps:
            st.warning("Nenhuma volta válida encontrada para esta sessão.")
            continue

        st.dataframe(
            ranked_laps_to_dataframe(track.ranked_laps),
            hide_index=True,
            column_config=LAPS_COLUMN_CONFIG,
        )
