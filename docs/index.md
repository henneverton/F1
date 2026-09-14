# F1 — Top 5 voltas mais rápidas

Dashboard web local, construído com [Streamlit](https://streamlit.io/), que
mostra as **cinco voltas válidas mais rápidas** de uma pista e sessão de
Fórmula 1 selecionadas pelo utilizador. Os dados vêm da
[OpenF1 API](https://openf1.org/docs/), um projeto não oficial e sem
afiliação com a Fórmula 1.

## Funcionalidades

- Filtros em cascata na barra lateral: época → pista/Grande Prémio → sessão.
- Tabela com posição, piloto, equipa, número, volta, tempo formatado
  (`m:ss.mmm`) e tempos de setor quando disponíveis.
- Gráfico de barras horizontais comparando as cinco voltas mais rápidas.
- Estados claros de carregamento vazio e de erro da API.

## Próximos passos

- [Instalação](instalacao.md) — como preparar o ambiente com pyenv e Poetry.
- [Uso do dashboard](uso-do-dashboard.md) — como executar e interpretar o
  dashboard.
- [Regras do ranking](regras-do-ranking.md) — critérios de validade e
  desempate usados no ranking.
- [Desenvolvimento](desenvolvimento.md) — como contribuir, testar e manter a
  qualidade do código.

## Aviso legal

A OpenF1 é um projeto não oficial, independente e sem qualquer associação
com as empresas de Fórmula 1.
