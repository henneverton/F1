"""Mapa do calendário: destaca no mapa-múndi o país selecionado."""

from __future__ import annotations

import altair as alt

WORLD_ATLAS_URL = "https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json"

# Códigos numéricos ISO 3166-1 (com zeros à esquerda, como usados no topojson
# do world-atlas) dos países que já receberam Grandes Prémios na OpenF1 API.
COUNTRY_ISO_NUMERIC: dict[str, str] = {
    "Australia": "036",
    "Austria": "040",
    "Azerbaijan": "031",
    "Bahrain": "048",
    "Belgium": "056",
    "Brazil": "076",
    "Canada": "124",
    "China": "156",
    "Hungary": "348",
    "Italy": "380",
    "Japan": "392",
    "Mexico": "484",
    "Monaco": "492",
    "Netherlands": "528",
    "Qatar": "634",
    "Saudi Arabia": "682",
    "Singapore": "702",
    "Spain": "724",
    "United Arab Emirates": "784",
    "United Kingdom": "826",
    "United States": "840",
}


def country_iso_id(country_name: str) -> str | None:
    """Devolve o código numérico ISO do país, ou `None` se for desconhecido."""

    return COUNTRY_ISO_NUMERIC.get(country_name)


def build_calendar_map(
    calendar_countries: list[str], selected_country: str | None
) -> alt.LayerChart:
    """Constrói um mapa-múndi com os países da época e o país selecionado em destaque.

    Os restantes países do calendário aparecem num tom intermédio, servindo de
    contexto, enquanto o país selecionado é pintado de vermelho.
    """

    world = alt.topo_feature(WORLD_ATLAS_URL, "countries")

    calendar_ids = sorted(
        {iso_id for name in calendar_countries if (iso_id := country_iso_id(name))}
    )
    selected_id = country_iso_id(selected_country) if selected_country else None

    layers = [alt.Chart(world).mark_geoshape(fill="#e5e7eb", stroke="#ffffff", strokeWidth=0.6)]

    if calendar_ids:
        layers.append(
            alt.Chart(world)
            .transform_filter(alt.FieldOneOfPredicate(field="id", oneOf=calendar_ids))
            .mark_geoshape(fill="#94a3b8", stroke="#ffffff", strokeWidth=0.6)
            .encode(tooltip=[alt.Tooltip("properties.name:N", title="País")])
        )

    if selected_id:
        layers.append(
            alt.Chart(world)
            .transform_filter(alt.FieldEqualPredicate(field="id", equal=selected_id))
            .mark_geoshape(fill="#e10600", stroke="#ffffff", strokeWidth=0.8)
            .encode(tooltip=[alt.Tooltip("properties.name:N", title="País selecionado")])
        )

    return alt.layer(*layers).project("naturalEarth1").properties(height=340)
