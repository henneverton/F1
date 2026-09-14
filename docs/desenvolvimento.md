# Desenvolvimento

## Estrutura do projeto

```text
src/f1/
├── __init__.py
├── app.py            # Ponto de entrada Streamlit
├── models.py          # Dataclasses de domínio
├── openf1_client.py   # Cliente HTTP da OpenF1 API
└── ranking.py          # Regras de ranking das voltas mais rápidas
tests/
├── fixtures/           # Respostas simuladas da OpenF1 API
├── test_openf1_client.py
├── test_ranking.py
└── test_app.py
docs/
mkdocs.yml
```

## Atalhos com taskipy

O grupo `dev` inclui [taskipy](https://github.com/taskipy/taskipy), que expõe
os comandos abaixo como `poetry run task <nome>`:

| Comando | Equivale a |
| --- | --- |
| `poetry run task lint` | `ruff check .` |
| `poetry run task format` | `ruff format .` |
| `poetry run task test` | `pytest` |
| `poetry run task cov` | `pytest --cov=src/f1 --cov-report=term-missing` |
| `poetry run task docs` | `mkdocs serve` |
| `poetry run task docs-build` | `mkdocs build --strict` |
| `poetry run task run` | `streamlit run src/f1/app.py` |

Use `poetry run task --list` para ver a lista completa. Os comandos Poetry
equivalentes continuam disponíveis e são usados no restante desta página.

## Qualidade de código

Ruff é a única ferramenta de lint e formatação:

```bash
poetry run ruff check . --fix
poetry run ruff format .
```

## Testes e cobertura

```bash
poetry run pytest
poetry run pytest --cov=src/f1 --cov-report=term-missing
```

Os testes nunca chamam a OpenF1 API real:

- `test_openf1_client.py` usa `httpx.MockTransport` para simular
  respostas HTTP (sucesso, lista vazia, erro HTTP, timeout, JSON inválido).
- `test_ranking.py` testa a função pura de ranking com dados em memória.
- `test_app.py` usa `streamlit.testing.v1.AppTest` para testar o dashboard
  de ponta a ponta, substituindo os métodos do `OpenF1Client` por versões
  simuladas via `monkeypatch`.

A cobertura mínima exigida sobre `src/f1` é de 50%.

## Documentação

```bash
poetry run mkdocs serve   # servidor local para escrever
poetry run mkdocs build --strict   # validação antes do PR
```

## Checklist antes do Pull Request

```bash
poetry run ruff check .
poetry run ruff format --check .
poetry run pytest
poetry run pytest --cov=src/f1 --cov-report=term-missing
poetry run mkdocs build --strict
poetry run streamlit run src/f1/app.py
```
