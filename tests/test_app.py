"""Testes de apresentação do dashboard, isolando a OpenF1 API."""

from __future__ import annotations

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from f1 import openf1_client
from f1.models import Driver, Lap, Meeting, Session, SessionResult
from f1.openf1_client import OpenF1Error

APP_PATH = "../src/f1/app.py"

MEETING = Meeting(
    meeting_key=1219,
    meeting_name="Singapore Grand Prix",
    circuit_short_name="Singapore",
    country_name="Singapore",
    year=2026,
    date_start="2026-10-02T09:30:00+00:00",
)
OTHER_COUNTRY_MEETING = Meeting(
    meeting_key=1220,
    meeting_name="Italian Grand Prix",
    circuit_short_name="Monza",
    country_name="Italy",
    year=2026,
    date_start="2026-09-06T09:30:00+00:00",
)
PRACTICE_SESSION = Session(
    session_key=9165,
    meeting_key=1219,
    session_name="Practice 1",
    session_type="Practice",
    date_start="2026-10-01T09:30:00+00:00",
)
RACE_SESSION = Session(session_key=9168, meeting_key=1219, session_name="Race", session_type="Race")
DRIVERS = [
    Driver(driver_number=1, full_name="Max Verstappen", team_name="Red Bull Racing"),
    Driver(driver_number=16, full_name="Charles Leclerc", team_name="Ferrari"),
]
FAST_LAPS = [
    Lap(driver_number=1, lap_number=10, lap_duration=91.0),
    Lap(driver_number=16, lap_number=11, lap_duration=90.5),
]
RACE_RESULT = [
    SessionResult(driver_number=16, position=1),
    SessionResult(driver_number=1, position=2),
]


@pytest.fixture(autouse=True)
def _clear_streamlit_caches():
    st.cache_data.clear()
    st.cache_resource.clear()
    yield


def _patch_client(
    monkeypatch,
    *,
    meetings=None,
    sessions=None,
    drivers=None,
    laps=None,
    session_results=None,
    meetings_error=None,
    laps_error=None,
):
    def get_meetings(self, year):
        if meetings_error:
            raise meetings_error
        return meetings if meetings is not None else []

    def get_sessions(self, meeting_key):
        return sessions if sessions is not None else []

    def get_drivers(self, session_key):
        return drivers if drivers is not None else []

    def get_laps(self, session_key):
        if laps_error:
            raise laps_error
        return laps if laps is not None else []

    def get_session_results(self, session_key):
        return session_results if session_results is not None else []

    monkeypatch.setattr(openf1_client.OpenF1Client, "get_meetings", get_meetings)
    monkeypatch.setattr(openf1_client.OpenF1Client, "get_sessions", get_sessions)
    monkeypatch.setattr(openf1_client.OpenF1Client, "get_drivers", get_drivers)
    monkeypatch.setattr(openf1_client.OpenF1Client, "get_laps", get_laps)
    monkeypatch.setattr(openf1_client.OpenF1Client, "get_session_results", get_session_results)


def test_dashboard_shows_top_laps_for_the_single_track(monkeypatch):
    _patch_client(
        monkeypatch,
        meetings=[MEETING],
        sessions=[PRACTICE_SESSION, RACE_SESSION],
        drivers=DRIVERS,
        laps=FAST_LAPS,
        session_results=RACE_RESULT,
    )

    at = AppTest.from_file(APP_PATH).run(timeout=15)

    assert not at.exception
    tracks_table = at.dataframe[0].value
    assert len(tracks_table) == 1
    assert tracks_table.iloc[0]["country_name"] == "Singapore"

    result = at.dataframe[1].value
    assert len(result) == 2
    assert result.iloc[0]["driver_name"] == "Charles Leclerc"
    assert result.iloc[1]["driver_name"] == "Max Verstappen"


def test_top_drivers_chart_reflects_wins_for_the_filtered_sessions(monkeypatch):
    _patch_client(
        monkeypatch,
        meetings=[MEETING],
        sessions=[RACE_SESSION],
        drivers=DRIVERS,
        laps=FAST_LAPS,
        session_results=RACE_RESULT,
    )

    at = AppTest.from_file(APP_PATH).run(timeout=15)

    assert not at.exception
    assert any("Top 3 pilotos" in md.value for md in at.markdown)
    # Há um vencedor (Charles Leclerc), logo o gráfico é desenhado em vez do aviso.
    assert not any("Sem vitórias" in info.value for info in at.info)
    assert at.get("vega_lite_chart")


def test_top_drivers_shows_info_when_no_wins_available(monkeypatch):
    _patch_client(
        monkeypatch,
        meetings=[MEETING],
        sessions=[RACE_SESSION],
        drivers=DRIVERS,
        laps=FAST_LAPS,
        session_results=[],
    )

    at = AppTest.from_file(APP_PATH).run(timeout=15)

    assert not at.exception
    assert any("Sem vitórias" in info.value for info in at.info)


def test_country_filter_narrows_both_tracks_list_and_lap_cards(monkeypatch):
    _patch_client(
        monkeypatch,
        meetings=[MEETING, OTHER_COUNTRY_MEETING],
        sessions=[RACE_SESSION],
        drivers=DRIVERS,
        laps=FAST_LAPS,
    )

    at = AppTest.from_file(APP_PATH).run(timeout=15)
    assert not at.exception

    country_select = at.selectbox[1]
    assert country_select.label == "País"
    assert set(country_select.options) == {"Todos os países", "Italy", "Singapore"}

    # Sem filtro, a lista de pistas e os cartões de voltas cobrem toda a época
    # (Itália antes de Singapura, por ordem de data).
    tracks_table = at.dataframe[0].value
    assert list(tracks_table["country_name"]) == ["Italy", "Singapore"]
    assert len(at.dataframe) == 3

    at = country_select.select("Singapore").run(timeout=15)

    assert not at.exception
    tracks_table = at.dataframe[0].value
    assert len(tracks_table) == 1
    assert tracks_table.iloc[0]["country_name"] == "Singapore"
    # Só um cartão de voltas (Singapura) deve restar, além da tabela de pistas.
    assert len(at.dataframe) == 2


def test_session_type_filter_changes_session_used(monkeypatch):
    _patch_client(
        monkeypatch,
        meetings=[MEETING],
        sessions=[PRACTICE_SESSION, RACE_SESSION],
        drivers=DRIVERS,
        laps=FAST_LAPS,
    )

    at = AppTest.from_file(APP_PATH).run(timeout=15)
    session_type_select = at.selectbox[2]
    assert session_type_select.label == "Tipo de sessão"

    at = session_type_select.select("Practice").run(timeout=15)

    assert not at.exception
    assert any("Practice 1" in caption.value for caption in at.caption)


def test_dashboard_shows_info_when_no_meetings(monkeypatch):
    _patch_client(monkeypatch, meetings=[])

    at = AppTest.from_file(APP_PATH).run(timeout=15)

    assert not at.exception
    assert at.info


def test_dashboard_shows_warning_when_no_valid_laps(monkeypatch):
    _patch_client(
        monkeypatch,
        meetings=[MEETING],
        sessions=[RACE_SESSION],
        drivers=DRIVERS,
        laps=[],
    )

    at = AppTest.from_file(APP_PATH).run(timeout=15)

    assert not at.exception
    assert at.warning


def test_dashboard_shows_error_on_api_failure(monkeypatch):
    _patch_client(monkeypatch, meetings_error=OpenF1Error("falha simulada"))

    at = AppTest.from_file(APP_PATH).run(timeout=15)

    assert not at.exception
    assert at.error
