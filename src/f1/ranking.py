"""Regras de domínio para o ranking das voltas mais rápidas."""

from __future__ import annotations

from f1.models import Driver, Lap, RankedLap

TOP_N = 5


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
