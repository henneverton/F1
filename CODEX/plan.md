# Plano de criação — dashboard das 5 voltas mais rápidas por pista

## Objetivo

Criar um dashboard web em Python que mostre, para a pista e sessão selecionadas, as **cinco voltas válidas mais rápidas** registadas na OpenF1 API. O utilizador poderá filtrar a época, o Grande Prémio/circuito e o tipo de sessão; o dashboard apresentará o ranking em tabela e gráfico, com piloto, equipa, tempo de volta, posição e detalhes de setores quando disponíveis.

O plano usa [doc_api.md](doc_api.md) como fonte funcional da OpenF1 API e segue integralmente os padrões de desenvolvimento em [SKILL.md](SKILL.md).

## Definição funcional

Uma “pista” é identificada pelo meeting/circuito retornado pelo endpoint `meetings`. As voltas serão obtidas por `session_key` no endpoint `laps`, pois a API relaciona sessões e meetings por `session_key` e `meeting_key`.

Para evitar resultados ambíguos, o MVP adota as seguintes regras:

- O ranking é das cinco menores durações de volta de uma **sessão selecionada** em uma pista.
- O mesmo piloto pode ocupar mais de uma posição caso tenha várias voltas entre as cinco melhores.
- Voltas sem duração não entram no ranking.
- Voltas de saída de boxes e outros dados marcados como não competitivos serão excluídos quando esse indicador estiver disponível no payload.
- A sessão de corrida será a seleção inicial recomendada, mas o utilizador poderá escolher prática, qualificação ou sprint quando existirem.

Comparar recordes históricos de uma mesma pista entre épocas será uma extensão futura, pois requer definir regras explícitas para mudanças de traçado, sessões e condições de pista.

## Escopo do MVP

- Dashboard local com Streamlit.
- Filtros de época, meeting/pista e sessão.
- Consulta encadeada: `meetings` → `sessions` → `drivers` e `laps`.
- Ranking das 5 voltas válidas mais rápidas por pista e sessão.
- Tabela com posição, piloto, equipa, número, volta, tempo e setores disponíveis.
- Gráfico de barras horizontais, ordenado da volta mais rápida para a quinta.
- Estados de carregamento, resultado vazio e erro da API compreensíveis.
- Testes unitários sem rede, Ruff sem erros e cobertura mínima de 50% sobre `src/projeto`.
- Documentação de execução e das regras do ranking.

Ficam fora do MVP: autenticação, dados em tempo real pagos, banco de dados, comparação histórica automática, telemetria (`car_data`), mapa de localização e publicação em ambiente de produção.

## Decisões de arquitetura

| Tema | Decisão |
| --- | --- |
| Interface | Streamlit, por fornecer um dashboard Python local com filtros e gráficos sem criar frontend separado. |
| Código | `src/projeto/`, com módulos independentes para cliente OpenF1, domínio/ranking e interface. |
| Dependências | Poetry exclusivamente; `httpx` e `streamlit` em produção. Ruff, pytest, pytest-cov e MkDocs Material no grupo `dev`. |
| Fonte de dados | Base `https://api.openf1.org/v1`; JSON como formato padrão. |
| Consulta | `meetings` para pistas, `sessions` para a sessão, `drivers` para nomes/equipas e `laps` para tempos. |
| Ranking | Ordenação crescente por duração de volta, depois corte dos cinco primeiros registos válidos. |
| Tipagem | Type hints em toda API interna/pública e modelos com `dataclass` para dados estáveis. |
| Testes | pytest com respostas HTTP simuladas; testes unitários nunca chamam a OpenF1 API. |

## Etapas de implementação

### 1. Preparar o ambiente e a estrutura

- [ ] Fixar a versão do Python com `pyenv local` de acordo com `pyproject.toml`.
- [ ] Configurar Poetry para empacotar `projeto` a partir de `src/`.
- [ ] Criar `src/projeto/__init__.py` e os módulos iniciais.
- [ ] Adicionar `httpx` e `streamlit` com `poetry add`.
- [ ] Adicionar `ruff`, `pytest`, `pytest-cov` e `mkdocs-material` ao grupo `dev` com Poetry.
- [ ] Aplicar em `pyproject.toml` as configurações de Ruff, pytest e coverage definidas em [SKILL.md](SKILL.md).
- [ ] Executar `poetry install` para criar e gerir automaticamente a virtualenv.

**Critério de aceite:** `poetry run python -c "import projeto"` funciona; o projeto não usa `pip`, `venv` nem `requirements.txt`.

### 2. Implementar o acesso à OpenF1 API

- [ ] Criar `src/projeto/openf1_client.py` com a URL-base, timeout e tratamento centralizado de erros HTTP/JSON.
- [ ] Implementar `get_meetings(year: int)` para carregar as pistas de uma época.
- [ ] Implementar `get_sessions(meeting_key: int | str)` para listar sessões de um meeting.
- [ ] Implementar `get_drivers(session_key: int | str)` para complementar o ranking com piloto, equipa e número.
- [ ] Implementar `get_laps(session_key: int | str)` para obter dados de volta da sessão.
- [ ] Reutilizar uma única instância de `httpx.Client` e garantir o seu fechamento.

**Critério de aceite:** o cliente devolve dados tipados ou lança exceções próprias para timeout, resposta HTTP malsucedida e JSON inválido.

### 3. Implementar regras de domínio e ranking

- [ ] Criar `src/projeto/models.py` para meeting, sessão, piloto, volta e item do ranking.
- [ ] Criar `src/projeto/ranking.py` com uma função pura que recebe voltas e pilotos e retorna as cinco melhores voltas.
- [ ] Descartar registros sem duração de volta e aplicar a regra de exclusão de voltas não competitivas quando o payload a disponibilizar.
- [ ] Converter a duração para um formato legível (`m:ss.mmm`) sem perder o valor numérico usado na ordenação.
- [ ] Associar cada volta ao piloto pelo número e usar valores de fallback claros quando a API não fornecer nome, equipa ou setor.
- [ ] Desempatar tempos iguais de modo determinístico, por exemplo por número da volta e número do piloto.

**Critério de aceite:** uma coleção de voltas conhecida produz exatamente cinco itens ordenados, com filtro de dados inválidos e formatação correta.

### 4. Construir o dashboard

- [ ] Criar o ponto de entrada `src/projeto/app.py`, executável por `poetry run streamlit run src/projeto/app.py`.
- [ ] Exibir os filtros na barra lateral: época, pista/Grande Prémio e sessão.
- [ ] Carregar os filtros em cascata: época → meetings → sessions.
- [ ] Mostrar título contextual com nome da pista, sessão e data/hora quando disponível.
- [ ] Exibir a tabela “Top 5 voltas mais rápidas” com as colunas de ranking definidas no escopo.
- [ ] Exibir gráfico de barras horizontais; a escala deve permitir comparar diferenças pequenas entre tempos.
- [ ] Mostrar mensagem orientativa quando não houver voltas válidas e ação de recarregar em caso de erro recuperável.
- [ ] Usar cache de curta duração apenas para reduzir chamadas repetidas da mesma seleção, sem esconder mudanças de filtros.

**Critério de aceite:** ao selecionar uma época, uma pista e uma sessão com dados, o dashboard mostra tabela e gráfico coerentes com a mesma ordenação.

### 5. Testar e validar qualidade

- [ ] Criar testes para o cliente: URLs, filtros, sucesso, lista vazia, erro HTTP, timeout e JSON inválido.
- [ ] Criar testes para o ranking: ordenação, limite de cinco, valores ausentes, voltas excluídas e desempate.
- [ ] Criar testes para a camada de apresentação que validem estados sem dados e dados formatados, isolando chamadas externas.
- [ ] Executar `poetry run ruff check . --fix` e `poetry run ruff format .`.
- [ ] Executar `poetry run pytest` e gerar relatório com `poetry run pytest --cov=src/projeto --cov-report=term-missing`.

**Critério de aceite:** todos os testes passam, Ruff não reporta problemas e a cobertura em `src/projeto` é igual ou superior a 50%.

### 6. Documentar e entregar

- [ ] Criar `mkdocs.yml` e as páginas em `docs/` usando MkDocs Material.
- [ ] Documentar instalação com pyenv e Poetry, dependências e como iniciar o dashboard.
- [ ] Documentar a origem OpenF1, o fluxo de dados, os filtros e as regras de validade/ranking das voltas.
- [ ] Informar que dados históricos são gratuitos desde 2023 e que dados em tempo real podem exigir subscrição.
- [ ] Documentar limitações: cobertura de dados, sessão sem voltas válidas e comparação histórica fora do MVP.
- [ ] Validar com `poetry run mkdocs build --strict` e atualizar o README com o comando de arranque.

**Critério de aceite:** uma pessoa nova consegue instalar, executar e interpretar o dashboard apenas com a documentação.

## Estrutura alvo

```text
src/projeto/
├── __init__.py
├── app.py
├── models.py
├── openf1_client.py
└── ranking.py
tests/
├── fixtures/
│   ├── drivers.json
│   ├── laps.json
│   ├── meetings.json
│   └── sessions.json
├── test_openf1_client.py
├── test_ranking.py
└── test_app.py
docs/
├── index.md
├── instalacao.md
├── uso-do-dashboard.md
├── regras-do-ranking.md
└── desenvolvimento.md
mkdocs.yml
```

## Verificação antes do Pull Request

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
poetry run pytest --cov=src/projeto --cov-report=term-missing
poetry run mkdocs build --strict
poetry run streamlit run src/projeto/app.py
```

O Pull Request deve indicar os endpoints usados, a regra de exclusão de voltas aplicada, a cobertura obtida e uma captura do dashboard para uma pista/sessão com dados.
