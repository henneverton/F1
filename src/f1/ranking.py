"""Regras de domínio para o ranking das voltas mais rápidas."""

from __future__ import annotations

from dataclasses import dataclass

from f1.models import Driver, Lap, RankedLap, SessionResult

TOP_N = 5
TOP_DRIVERS_N = 3


@dataclass(frozen=True, slots=True)
class DriverWinTally:
    """Contagem de vitórias (posição 1) de um piloto num conjunto de sessões."""

    driver_number: int
    driver_name: str
    team_name: str
    wins: int


def format_lap_duration(seconds: float) -> str:
    """Formata uma duração em segundos como `m:ss.mmm`."""

    minutes, remainder = divmod(seconds, 60)
    return f"{int(minutes)}:{remainder:06.3f}"


def rank_fastest_laps(
    laps: list[Lap], drivers: list[Driver], top_n: int = TOP_N
) -> list[RankedLap]:
    """Retorna as `top_n` voltas válidas mais rápidas, ordenadas da mais rápida.

    Voltas sem duração ou marcadas como saída de boxes são descartadas. Em
    caso de empate, o desempate é feito por número da volta e depois por
    número do piloto, para um resultado determinístico.
    """

    drivers_by_number = {driver.driver_number: driver for driver in drivers}

    valid_laps = [lap for lap in laps if lap.lap_duration is not None and not lap.is_pit_out_lap]
    ordered_laps = sorted(
        valid_laps,
        key=lambda lap: (lap.lap_duration, lap.lap_number, lap.driver_number),
    )

    ranked: list[RankedLap] = []
    for position, lap in enumerate(ordered_laps[:top_n], start=1):
        driver = drivers_by_number.get(lap.driver_number)
        ranked.append(
            RankedLap(
                position=position,
                driver_number=lap.driver_number,
                driver_name=driver.full_name if driver else f"Piloto #{lap.driver_number}",
                team_name=(driver.team_name if driver and driver.team_name else "Desconhecida"),
                lap_number=lap.lap_number,
                lap_duration=lap.lap_duration,
                lap_duration_formatted=format_lap_duration(lap.lap_duration),
                duration_sector_1=lap.duration_sector_1,
                duration_sector_2=lap.duration_sector_2,
                duration_sector_3=lap.duration_sector_3,
            )
        )

    return ranked


def tally_wins(
    sessions_data: list[tuple[list[SessionResult], list[Driver]]], top_n: int = TOP_DRIVERS_N
) -> list[DriverWinTally]:
    """Conta vitórias (posição 1) por piloto num conjunto de sessões e devolve o top.

    Cada item de `sessions_data` é um par (classificação, pilotos) de uma
    sessão. Em caso de empate no número de vitórias, o desempate é feito por
    nome do piloto, para um resultado determinístico.
    """

    drivers_by_number: dict[int, Driver] = {}
    wins_by_number: dict[int, int] = {}

    for results, drivers in sessions_data:
        for driver in drivers:
            drivers_by_number.setdefault(driver.driver_number, driver)
        for result in results:
            if result.position == 1:
                wins_by_number[result.driver_number] = (
                    wins_by_number.get(result.driver_number, 0) + 1
                )

    tallies = [
        DriverWinTally(
            driver_number=number,
            driver_name=(
                drivers_by_number[number].full_name
                if number in drivers_by_number
                else f"Piloto #{number}"
            ),
            team_name=(
                drivers_by_number[number].team_name
                if number in drivers_by_number and drivers_by_number[number].team_name
                else "Desconhecida"
            ),
            wins=wins,
        )
        for number, wins in wins_by_number.items()
    ]

    return sorted(tallies, key=lambda t: (-t.wins, t.driver_name))[:top_n]
