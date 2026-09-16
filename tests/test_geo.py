"""Testes do mapa do calendário (destaque do país selecionado)."""

from __future__ import annotations

from f1.geo import build_calendar_map, country_iso_id


def test_country_iso_id_known_country():
    assert country_iso_id("Singapore") == "702"


def test_country_iso_id_unknown_country_returns_none():
    assert country_iso_id("Wakanda") is None


def test_build_calendar_map_has_one_layer_per_known_group():
    chart = build_calendar_map(["Singapore", "Monaco"], "Monaco")
    spec = chart.to_dict()

    # fundo do mundo + países do calendário + país selecionado
    assert len(spec["layer"]) == 3
    filters = [layer["transform"][0]["filter"] for layer in spec["layer"][1:]]
    assert filters[0] == {"field": "id", "oneOf": ["492", "702"]}
    assert filters[1] == {"field": "id", "equal": "492"}


def test_build_calendar_map_without_selection_omits_highlight_layer():
    chart = build_calendar_map(["Singapore"], None)
    spec = chart.to_dict()

    assert len(spec["layer"]) == 2


def test_build_calendar_map_ignores_unknown_countries():
    chart = build_calendar_map(["Wakanda"], "Wakanda")
    spec = chart.to_dict()

    # nenhum país reconhecido: só o fundo do mundo permanece
    assert len(spec["layer"]) == 1
