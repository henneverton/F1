"""Retoques visuais do dashboard: CSS e ilustração da barra lateral."""

from __future__ import annotations

SIDEBAR_CAR_SVG = """
<div style="text-align:center; margin: -0.5rem 0 0.75rem;">
  <svg width="130" height="58" viewBox="0 0 200 80" xmlns="http://www.w3.org/2000/svg"
       role="img" aria-label="Ilustração de um carro de Fórmula 1">
    <defs>
      <linearGradient id="f1CarGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#ff9aac"/>
        <stop offset="55%" stop-color="#ffcf9a"/>
        <stop offset="100%" stop-color="#9adcff"/>
      </linearGradient>
    </defs>
    <rect x="150" y="16" width="30" height="7" rx="2.5" fill="url(#f1CarGradient)"/>
    <rect x="173" y="8" width="6" height="28" rx="2" fill="url(#f1CarGradient)"/>
    <path d="M18 56
             C18 46 34 40 56 40
             L118 40
             C132 40 138 30 154 27
             L169 30
             C173 34 171 43 165 47
             L148 52
             L60 56
             Z" fill="url(#f1CarGradient)"/>
    <rect x="8" y="53" width="32" height="7" rx="2.5" fill="url(#f1CarGradient)"/>
    <path d="M84 40 C89 25 106 25 113 40" stroke="url(#f1CarGradient)" stroke-width="5"
          fill="none" stroke-linecap="round"/>
    <circle cx="55" cy="59" r="15" fill="#4a4658"/>
    <circle cx="55" cy="59" r="7" fill="#7a7690"/>
    <circle cx="152" cy="59" r="17" fill="#4a4658"/>
    <circle cx="152" cy="59" r="8" fill="#7a7690"/>
  </svg>
</div>
"""

CUSTOM_CSS = """
<style>
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #fdf1f4 0%, #f3ecfb 50%, #eaf4fb 100%);
}

[data-testid="stSidebar"] * {
    color: #3a3450 !important;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div,
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div {
    background: linear-gradient(
        135deg, rgba(255, 154, 172, 0.35), rgba(255, 207, 154, 0.3), rgba(154, 220, 255, 0.35)
    );
    backdrop-filter: blur(6px);
    border: 1px solid rgba(255, 255, 255, 0.6);
    border-radius: 999px;
    transition: transform 0.15s ease, box-shadow 0.15s ease;
}

[data-testid="stSidebar"] [data-testid="stSelectbox"] > div > div:hover,
[data-testid="stSidebar"] [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover {
    transform: translateY(-1px);
    box-shadow: 0 4px 14px rgba(154, 140, 200, 0.25);
}

h1 {
    background: linear-gradient(90deg, #ff8fa3, #ffc785, #7fd1ff);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent !important;
}

.st-key-map_card,
.st-key-top_drivers_card,
.st-key-tracks_card,
[class*="st-key-laps_card_"] {
    background: linear-gradient(135deg, rgba(255, 154, 172, 0.07), rgba(154, 220, 255, 0.07));
    border-radius: 16px;
}
</style>
"""
