# OpenF1 API — resumo

Documentação oficial: <https://openf1.org/docs/>
Base URL: `https://api.openf1.org/v1`

## 1. Introdução

- API não oficial e open-source (código em `br-g/openf1`) para dados de telemetria, cronometragem e sessões da Fórmula 1, em JSON ou CSV.
- Dados históricos desde 2023 são gratuitos e não exigem autenticação.
- A API é independente da Formula 1 e não tem afiliação oficial com as empresas de F1.

## 2. Autenticação

- **Dados históricos:** acesso livre, sem chave ou autenticação.
- **Dados em tempo real:** exigem subscrição paga.

## 3. Fluxo recomendado de consulta

1. Consulte `meetings` para encontrar o Grande Prémio.
2. Consulte `sessions` para obter a sessão desejada e respetivo `session_key`.
3. Use `drivers` para identificar pilotos e números.
4. Consulte os endpoints específicos de corrida, estratégia, telemetria ou condições.

Exemplo:

```bash
curl "https://api.openf1.org/v1/sessions?year=2026&country_name=Singapore"
```

## 4. Endpoints

### `meetings`
Informação de cada fim de semana (GP ou teste): `circuit_key`, `circuit_short_name`, `country_name`, `date_start`, `date_end`, `is_cancelled`, `location`, `meeting_key`, `year`. Campos adicionais: `circuit_image`, `circuit_info_url` (dados do FastF1), `gmt_offset`. Atualizado diariamente à meia-noite UTC.

### `sessions`
Sessões de um meeting (prática, qualificação, sprint, corrida): `circuit_key`, `country_name`, `date_start`, `date_end`, `session_name`, `session_type`, `is_cancelled`, `year`. Atualizado diariamente à meia-noite UTC.

### `drivers`
Pilotos de uma sessão: `broadcast_name`, `driver_number`, `first_name`, `full_name`, `headshot_url`, `team_name`, `team_colour`. Campo `country_code` **deprecado** (remoção prevista para o fim de 2026).

### `session_result`
Classificação oficial após a sessão (disponível poucos minutos depois): `driver_number`, `position`, `duration`, `gap_to_leader`, `dnf`, `dns`, `dsq`, `number_of_laps`. Em qualificação, `duration` é um array `[Q1, Q2, Q3]`.

### `starting_grid`
Grelha de partida da corrida: `position`, `driver_number`, `lap_duration`.

### `position`
Evolução da posição de cada piloto durante a sessão: `date`, `driver_number`, `position`.

### `intervals`
Intervalo para o carro da frente e diferença para o líder; apenas em corrida, atualizado a cada ~4 s: `date`, `driver_number`, `gap_to_leader`, `interval`. O líder recebe `null`; um piloto voltado é marcado como `"+1 LAP"`.

### `laps`
Detalhe por volta: `date_start`, `duration_sector_1/2/3`, `i1_speed`, `i2_speed`, `is_pit_out_lap`, `lap_duration`, `lap_number`, `segments_sector_1/2/3`, `st_speed` (speed trap). Códigos de segmento: `2048` amarelo, `2049` verde, `2051` roxo (melhor), `2064` pit lane. Segmentos não ficam disponíveis durante corridas.

### `stints`
Estratégia de pneus: `compound` (`SOFT`, `MEDIUM`, `HARD`, entre outros), `driver_number`, `lap_start`, `lap_end`, `stint_number`, `tyre_age_at_start`.

### `pit`
Passagens pelas boxes: `date`, `driver_number`, `lap_number`, `lane_duration`, `stop_duration`. `stop_duration` disponível a partir do GP dos EUA de 2024. Campo `pit_duration` **deprecado**, substituído por `lane_duration`.

### `overtakes`
Registo de ultrapassagens (apenas corrida, pode estar incompleto): `date`, `overtaking_driver_number`, `overtaken_driver_number`, `position` (posição após a ultrapassagem). Inclui passagens em pista, mudanças por pit stop e penalidades.

### `race_control`
Mensagens do controlo de corrida: `category`, `date`, `flag`, `message`, `lap_number`, `scope`, `sector`, `qualifying_phase`. Categorias: `SessionStatus`, `CarEvent`, `Drs`, `Flag`, `SafetyCar`. Bandeiras: `GREEN`, `YELLOW`, `DOUBLE YELLOW`, `CHEQUERED`, `BLACK AND WHITE`, entre outras.

### `championship_drivers` *(beta)*
Pontos e posições do campeonato de pilotos; apenas sessões de corrida: `driver_number`, `points_current`, `points_start`, `position_current`, `position_start`.

### `championship_teams` *(beta)*
Pontos e posições do campeonato de construtores; apenas sessões de corrida: `team_name`, `points_current`, `points_start`, `position_current`, `position_start`.

### `car_data`
Telemetria do carro (~3,7 Hz): `brake`, `date`, `driver_number`, `drs`, `gear`, `rpm`, `speed`, `throttle`. Valores de `drs` variam de 0 a 14, com significados distintos (ex.: ativado, detetado, não disponível).

### `location`
Coordenadas 3D aproximadas na pista (~3,7 Hz): `date`, `driver_number`, `x`, `y`, `z`. A origem `(0,0,0)` é arbitrária e não corresponde a um ponto físico do circuito; não representam a posição lateral com precisão.

### `weather`
Clima na pista, atualizado a cada minuto: `air_temperature` (°C), `humidity` (%), `pressure` (mbar), `rainfall`, `track_temperature` (°C), `wind_direction` (0–359°), `wind_speed` (m/s).

### `team_radio`
Seleção limitada de rádios: `date`, `driver_number`, `recording_url`. **Aviso:** a cobertura diminuiu significativamente a partir de 2026, com a maioria dos eventos sem qualquer dado de rádio.

## 5. Filtros

Todos os endpoints aceitam parâmetros na query string e permitem filtrar por atributos simples (arrays não são filtráveis). Operadores disponíveis: `=`, `>`, `>=`, `<`, `<=`, `!=`. É possível combinar múltiplos filtros:

```text
?session_key=9165&driver_number=55
?speed>=315
?position<=3
?date_start>=2026-09-01&date_end<=2026-09-30
```

**Filtros por data/hora** aceitam vários formatos (ISO 8601, `DD/MM/YYYY`, texto natural), mas prefira ISO 8601 em UTC, por exemplo `2026-09-01T14:30:00+00:00`.

Os campos `meeting_key` e `session_key` ligam a maior parte dos recursos e aceitam `latest` para o evento ou sessão atual/mais recente.

## 6. Formato de resposta

- **JSON** (padrão): array de objetos.
- **CSV**: acrescente `csv=true` à query string, útil para abrir em Excel/Google Sheets. Exemplo: `?year=2026&csv=true`.

## 7. Observações e limitações importantes

- `driver_number` é o número do piloto na época; não deve ser tratado como identificador histórico universal.
- A telemetria (`car_data`) e a localização (`location`) têm grande volume: filtre por `session_key`, `driver_number` e intervalo de datas antes de descarregar.
- Campos obsoletos, com remoção prevista para o fim da época de 2026: `drivers.country_code` e `pit.pit_duration` (usar `lane_duration`).
- `intervals` e `championship_*` só estão disponíveis em sessões de corrida.
- Segmentos de volta (`laps.segments_sector_*`) não ficam disponíveis durante corridas.
- `team_radio` tem cobertura muito reduzida a partir de 2026.

## 8. Suporte

- Problemas técnicos: GitHub Issues do projeto.
- Suporte geral e dúvidas: GitHub Discussions.
- Código-fonte aberto disponível no repositório `br-g/openf1`.

## 9. Aviso legal

A OpenF1 é um projeto não oficial e não tem qualquer associação com as empresas da Formula 1.

---

Fonte: [documentação oficial da OpenF1](https://openf1.org/docs/), consultada em 14-09-2026.
