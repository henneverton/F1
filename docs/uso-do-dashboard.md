# Uso do dashboard

## Filtros

Os filtros ficam na barra lateral e são aplicados em cascata:

1. **Época** — anos de 2023 (início dos dados gratuitos da OpenF1) até o ano
   corrente.
2. **Pista / Grande Prémio** — meetings disponíveis na época escolhida.
3. **Sessão** — sessões do meeting (prática, qualificação, sprint ou
   corrida). Por omissão, a sessão de **corrida** é pré-selecionada quando
   existir.

## Conteúdo principal

- **Título contextual** com o nome da pista e da sessão selecionada, além da
  data de início quando disponível.
- **Tabela "Top 5 voltas mais rápidas"** com posição, piloto, equipa,
  número, número da volta, tempo formatado (`m:ss.mmm`) e tempos de setor
  (quando a OpenF1 disponibiliza esse dado para a sessão).
- **Gráfico de barras horizontais**, ordenado da volta mais rápida (topo)
  para a quinta, com escala ajustada para evidenciar pequenas diferenças de
  tempo entre os pilotos.

## Estados especiais

| Situação | Comportamento |
| --- | --- |
| Época sem Grandes Prémios registados | Mensagem informativa, sem tabela nem gráfico. |
| Pista sem sessões registadas | Mensagem informativa, sem tabela nem gráfico. |
| Sessão sem voltas válidas | Aviso a sugerir escolher outra sessão ou pista. |
| Falha ao comunicar com a OpenF1 API | Mensagem de erro com o motivo (tempo limite, erro HTTP ou resposta inválida); recarregue a página para tentar novamente. |

## Limitações conhecidas

- Apenas uma sessão é analisada de cada vez — comparações entre sessões ou
  épocas diferentes não fazem parte do MVP.
- Dados de telemetria (`car_data`) e mapa de localização não são exibidos.
- Segmentos de volta e tempos de setor podem não estar disponíveis durante
  corridas, conforme documentado pela OpenF1 API.
