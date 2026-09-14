"""Testes do cliente OpenF1: nunca tocam a rede, usam um transporte simulado."""

from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from f1.openf1_client import (
    OpenF1Client,
    OpenF1DecodeError,
    OpenF1HTTPError,
    OpenF1TimeoutError,
)

FIXTURES = Path(__file__).parent / "fixtures"


def _load_fixture(name: str) -> list[dict]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def _client_with_handler(handler) -> OpenF1Client:
    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(base_url="https://api.openf1.org/v1", transport=transport)
    return OpenF1Client(client=http_client)


def test_get_meetings_builds_url_and_filters_by_year():
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["path"] = request.url.path
        captured["params"] = dict(request.url.params)
        return httpx.Response(200, json=_load_fixture("meetings.json"))

    client = _client_with_handler(handler)
    meetings = client.get_meetings(2026)

    assert captured["path"] == "/v1/meetings"
    assert captured["params"] == {"year": "2026"}
    assert len(meetings) == 2
    assert meetings[0].meeting_name == "Singapore Grand Prix"
    assert meetings[0].year == 2026


def test_get_sessions_filters_by_meeting_key():
    def handler(request: httpx.Request) -> httpx.Response:
        assert dict(request.url.params) == {"meeting_key": "1219"}
        return httpx.Response(200, json=_load_fixture("sessions.json"))

    client = _client_with_handler(handler)
    sessions = client.get_sessions(1219)

    assert len(sessions) == 2
    assert sessions[1].session_name == "Race"


def test_get_drivers_success():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_load_fixture("drivers.json"))

    client = _client_with_handler(handler)
    drivers = client.get_drivers(9168)

    assert len(drivers) == 3
    assert drivers[0].full_name == "Max Verstappen"
    assert drivers[0].team_name == "Red Bull Racing"


def test_get_laps_success():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_load_fixture("laps.json"))

    client = _client_with_handler(handler)
    laps = client.get_laps(9168)

    assert len(laps) == 5
    assert laps[0].lap_duration == 91.234


def test_empty_result_returns_empty_list():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    client = _client_with_handler(handler)

    assert client.get_meetings(1900) == []


def test_http_error_raises_openf1_http_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="internal error")

    client = _client_with_handler(handler)

    with pytest.raises(OpenF1HTTPError):
        client.get_meetings(2026)


def test_timeout_raises_openf1_timeout_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out")

    client = _client_with_handler(handler)

    with pytest.raises(OpenF1TimeoutError):
        client.get_meetings(2026)


def test_invalid_json_raises_openf1_decode_error():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not json", headers={"content-type": "application/json"})

    client = _client_with_handler(handler)

    with pytest.raises(OpenF1DecodeError):
        client.get_meetings(2026)


def test_close_closes_underlying_http_client():
    closed = {"value": False}

    class FakeHttpClient:
        def close(self) -> None:
            closed["value"] = True

    client = OpenF1Client(client=FakeHttpClient())
    client.close()

    assert closed["value"] is True


def test_context_manager_closes_client():
    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    with _client_with_handler(handler) as client:
        assert client.get_meetings(2026) == []
