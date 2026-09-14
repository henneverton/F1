# Regras do ranking

O ranking mostra as **cinco menores durações de volta** de uma sessão
selecionada em uma pista, obtidas do endpoint `laps` da OpenF1 API
(filtrado por `session_key`).

## Fluxo de consulta

1. `meetings` — pistas/Grandes Prémios de uma época.
2. `sessions` — sessões de um meeting (`session_key`).
3. `drivers` — nomes e equipas dos pilotos de uma sessão.
4. `laps` — durações de volta da sessão.

## Critérios de validade

Uma volta só entra no ranking se:

- tiver uma duração (`lap_duration`) registada — voltas sem duração são
  descartadas;
- não for uma volta de saída de boxes (`is_pit_out_lap`), quando esse
  indicador estiver disponível no payload.

## Ordenação e desempate

As voltas válidas são ordenadas por duração crescente. Em caso de empate,
o desempate é determinístico, por:

1. número da volta (`lap_number`), crescente;
2. número do piloto (`driver_number`), crescente.

Apenas as cinco primeiras voltas da ordenação final compõem o ranking. O
mesmo piloto pode ocupar mais de uma posição, caso tenha várias voltas
entre as cinco melhores.

## Formatação

O tempo de volta é convertido para o formato `m:ss.mmm` (por exemplo,
`1:31.234`) apenas para exibição — a ordenação usa sempre o valor numérico
original, em segundos.

## Fora do escopo do MVP

- Comparar recordes históricos da mesma pista entre épocas diferentes,
  já que isso exige regras explícitas para mudanças de traçado, tipos de
  sessão e condições de pista.
- Considerar penalidades ou desqualificações aplicadas após a sessão.
