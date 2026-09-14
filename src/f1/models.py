"""Modelos de domínio para pistas, sessões, pilotos e voltas da OpenF1."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Meeting:
    """Um fim de semana de Grande Prémio (pista/circuito)."""

    meeting_key: int
    meeting_name: str
    circuit_short_name: str
    country_name: str
    year: int
    date_start: str | None = None


@dataclass(frozen=True, slots=True)
class Session:
    """Uma sessão (prática, qualificação, sprint ou corrida) de um meeting."""

    session_key: int
    meeting_key: int
    session_name: str
    session_type: str
    date_start: str | None = None


@dataclass(frozen=True, slots=True)
class Driver:
    """Um piloto participante de uma sessão."""

    driver_number: int
    full_name: str
    team_name: str | None = None


@dataclass(frozen=True, slots=True)
class Lap:
    """Uma volta registada durante uma sessão."""

    driver_number: int
    lap_number: int
    lap_duration: float | None
    is_pit_out_lap: bool = False
    duration_sector_1: float | None = None
    duration_sector_2: float | None = None
    duration_sector_3: float | None = None


@dataclass(frozen=True, slots=True)
class RankedLap:
    """Um item do ranking das voltas mais rápidas, pronto para exibição."""

    position: int
    driver_number: int
    driver_name: str
    team_name: str
    lap_number: int
    lap_duration: float
    lap_duration_formatted: str
    duration_sector_1: float | None = None
    duration_sector_2: float | None = None
    duration_sector_3: float | None = None
