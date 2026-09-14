"""Testes de apresentação do dashboard, isolando a OpenF1 API."""

from __future__ import annotations

import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

from f1 import openf1_client
from f1.models import Driver, Lap, Meeting, Session
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
PRACTICE_SESSION = Session(
    session_key=9165, meeting_key=1219, session_name="Practice 1", session_type="Practice"
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

    monkeypatch.setattr(openf1_client.OpenF1Client, "get_meetings", get_meetings)
    monkeypatch.setattr(openf1_client.OpenF1Client, "get_sessions", get_sessions)
    monkeypatch.setattr(openf1_client.OpenF1Client, "get_drivers", get_drivers)
    monkeypatch.setattr(openf1_client.OpenF1Client, "get_laps", get_laps)


def test_dashboard_shows_top_laps_table(monkeypatch):
    _patch_client(
        monkeypatch,
        meetings=[MEETING],
        sessions=[PRACTICE_SESSION, RACE_SESSION],
        drivers=DRIVERS,
        laps=FAST_LAPS,
    )

    at = AppTest.from_file(APP_PATH).run(timeout=15)

    assert not at.exception
    result = at.dataframe[0].value
    assert len(result) == 2
    assert result.iloc[0]["driver_name"] == "Charles Leclerc"
    assert result.iloc[1]["driver_name"] == "Max Verstappen"


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
