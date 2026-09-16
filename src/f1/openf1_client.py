"""Cliente HTTP para a OpenF1 API (https://api.openf1.org/v1)."""

from __future__ import annotations

import time
from typing import Any

import httpx

from f1.models import Driver, Lap, Meeting, Session, SessionResult

BASE_URL = "https://api.openf1.org/v1"
DEFAULT_TIMEOUT = 10.0

# A OpenF1 API limita a 3 pedidos/segundo; abaixo disso evitamos 429s quando o
# dashboard percorre várias pistas seguidas (uma pista = até 3 pedidos).
MIN_REQUEST_INTERVAL = 0.4
MAX_RATE_LIMIT_RETRIES = 3


class OpenF1Error(Exception):
    """Erro genérico ao comunicar com a OpenF1 API."""


class OpenF1TimeoutError(OpenF1Error):
    """A requisição excedeu o tempo limite."""


class OpenF1HTTPError(OpenF1Error):
    """A OpenF1 API respondeu com um código de erro HTTP."""


class OpenF1DecodeError(OpenF1Error):
    """A resposta da OpenF1 API não é um JSON válido."""


class OpenF1Client:
    """Cliente fino sobre a OpenF1 API, reutilizando uma única conexão HTTP."""

    def __init__(
        self,
        base_url: str = BASE_URL,
        timeout: float = DEFAULT_TIMEOUT,
        client: httpx.Client | None = None,
    ) -> None:
        self._base_url = base_url
        self._client = client or httpx.Client(base_url=base_url, timeout=timeout)
        self._last_request_at: float = 0.0

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> OpenF1Client:
        return self

    def __exit__(self, *_exc_info: object) -> None:
        self.close()

    def _throttle(self) -> None:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < MIN_REQUEST_INTERVAL:
            time.sleep(MIN_REQUEST_INTERVAL - elapsed)

    def _send(self, path: str, params: dict[str, Any]) -> httpx.Response:
        self._throttle()
        try:
            response = self._client.get(path, params=params)
        except httpx.TimeoutException as exc:
            raise OpenF1TimeoutError(f"Tempo limite ao consultar {path}") from exc
        except httpx.HTTPError as exc:
            raise OpenF1Error(f"Falha de rede ao consultar {path}: {exc}") from exc
        finally:
            self._last_request_at = time.monotonic()
        return response

    def _get(self, path: str, params: dict[str, Any]) -> list[dict[str, Any]]:
        response = self._send(path, params)

        for _ in range(MAX_RATE_LIMIT_RETRIES):
            if response.status_code != 429:
                break
            retry_after = float(response.headers.get("Retry-After", 1.0))
            time.sleep(retry_after)
            response = self._send(path, params)

        if response.status_code == 404:
            # A OpenF1 API responde 404 (em vez de 200 com lista vazia) quando o
            # filtro não corresponde a nenhum registo — não é um erro real.
            return []

        if response.status_code >= 400:
            raise OpenF1HTTPError(
                f"OpenF1 respondeu {response.status_code} para {path}: {response.text}"
            )

        try:
            data = response.json()
        except ValueError as exc:
            raise OpenF1DecodeError(f"Resposta inválida (não é JSON) para {path}") from exc

        if not isinstance(data, list):
            raise OpenF1DecodeError(f"Resposta inesperada (esperava lista) para {path}")

        return data

    def get_meetings(self, year: int) -> list[Meeting]:
        raw = self._get("/meetings", {"year": year})
        return [
            Meeting(
                meeting_key=item["meeting_key"],
                meeting_name=item.get("meeting_name") or item.get("circuit_short_name", ""),
                circuit_short_name=item.get("circuit_short_name", ""),
                country_name=item.get("country_name", ""),
                year=item.get("year", year),
                date_start=item.get("date_start"),
            )
            for item in raw
        ]

    def get_sessions(self, meeting_key: int | str) -> list[Session]:
        raw = self._get("/sessions", {"meeting_key": meeting_key})
        return [
            Session(
                session_key=item["session_key"],
                meeting_key=item["meeting_key"],
                session_name=item.get("session_name", ""),
                session_type=item.get("session_type", ""),
                date_start=item.get("date_start"),
            )
            for item in raw
        ]

    def get_drivers(self, session_key: int | str) -> list[Driver]:
        raw = self._get("/drivers", {"session_key": session_key})
        return [
            Driver(
                driver_number=item["driver_number"],
                full_name=item.get("full_name") or item.get("broadcast_name", "Desconhecido"),
                team_name=item.get("team_name"),
            )
            for item in raw
        ]

    def get_session_results(self, session_key: int | str) -> list[SessionResult]:
        raw = self._get("/session_result", {"session_key": session_key})
        return [
            SessionResult(
                driver_number=item["driver_number"],
                position=item.get("position"),
                dnf=bool(item.get("dnf", False)),
                dns=bool(item.get("dns", False)),
                dsq=bool(item.get("dsq", False)),
            )
            for item in raw
        ]

    def get_laps(self, session_key: int | str) -> list[Lap]:
        raw = self._get("/laps", {"session_key": session_key})
        return [
            Lap(
                driver_number=item["driver_number"],
                lap_number=item.get("lap_number", 0),
                lap_duration=item.get("lap_duration"),
                is_pit_out_lap=bool(item.get("is_pit_out_lap", False)),
                duration_sector_1=item.get("duration_sector_1"),
                duration_sector_2=item.get("duration_sector_2"),
                duration_sector_3=item.get("duration_sector_3"),
            )
            for item in raw
        ]
