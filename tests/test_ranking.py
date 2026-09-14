"""Testes das regras de domínio de ranking das voltas mais rápidas."""

from __future__ import annotations

from f1.models import Driver, Lap
from f1.ranking import format_lap_duration, rank_fastest_laps

DRIVERS = [
    Driver(driver_number=1, full_name="Max Verstappen", team_name="Red Bull Racing"),
    Driver(driver_number=16, full_name="Charles Leclerc", team_name="Ferrari"),
    Driver(driver_number=44, full_name="Lewis Hamilton", team_name="Ferrari"),
    Driver(driver_number=63, full_name="George Russell", team_name="Mercedes"),
]


def _lap(driver_number: int, lap_number: int, duration: float | None, pit_out: bool = False) -> Lap:
    return Lap(
        driver_number=driver_number,
        lap_number=lap_number,
        lap_duration=duration,
        is_pit_out_lap=pit_out,
    )


def test_format_lap_duration_formats_minutes_seconds_milliseconds():
    assert format_lap_duration(91.234) == "1:31.234"
    assert format_lap_duration(59.999) == "0:59.999"


def test_rank_returns_five_fastest_ordered_ascending():
    laps = [
        _lap(1, 10, 92.0),
        _lap(16, 11, 90.5),
        _lap(44, 12, 91.0),
        _lap(63, 13, 93.0),
        _lap(1, 14, 89.9),
        _lap(16, 15, 94.0),
    ]

    ranked = rank_fastest_laps(laps, DRIVERS)

    assert len(ranked) == 5
    assert [item.lap_duration for item in ranked] == sorted(item.lap_duration for item in ranked)
    assert ranked[0].driver_name == "Max Verstappen"
    assert ranked[0].position == 1
    assert ranked[-1].position == 5


def test_same_driver_can_occupy_multiple_positions():
    laps = [
        _lap(1, 10, 90.0),
        _lap(1, 11, 90.1),
        _lap(1, 12, 90.2),
        _lap(16, 13, 90.3),
        _lap(44, 14, 90.4),
    ]

    ranked = rank_fastest_laps(laps, DRIVERS)

    assert sum(1 for item in ranked if item.driver_number == 1) == 3


def test_laps_without_duration_are_excluded():
    laps = [
        _lap(1, 10, None),
        _lap(16, 11, 90.0),
    ]

    ranked = rank_fastest_laps(laps, DRIVERS)

    assert len(ranked) == 1
    assert ranked[0].driver_number == 16


def test_pit_out_laps_are_excluded():
    laps = [
        _lap(1, 10, 80.0, pit_out=True),
        _lap(16, 11, 95.0),
    ]

    ranked = rank_fastest_laps(laps, DRIVERS)

    assert len(ranked) == 1
    assert ranked[0].driver_number == 16


def test_ties_are_broken_deterministically_by_lap_then_driver():
    laps = [
        _lap(44, 20, 90.0),
        _lap(1, 10, 90.0),
        _lap(16, 15, 90.0),
    ]

    ranked = rank_fastest_laps(laps, DRIVERS)

    assert [item.driver_number for item in ranked] == [1, 16, 44]


def test_unknown_driver_falls_back_to_generic_label():
    laps = [_lap(99, 1, 88.0)]

    ranked = rank_fastest_laps(laps, DRIVERS)

    assert ranked[0].driver_name == "Piloto #99"
    assert ranked[0].team_name == "Desconhecida"


def test_empty_laps_returns_empty_ranking():
    assert rank_fastest_laps([], DRIVERS) == []
