---
name: padrao-desenvolvimento-python
description: Define o ambiente, qualidade, testes, documentação e fluxo oficial para contribuir neste projeto Python.
---

# Padrões oficiais de desenvolvimento

Este documento é a referência para configurar o ambiente e contribuir com o projeto. Todas as alterações devem seguir estas convenções.

## Princípios obrigatórios

- Use **pyenv** para selecionar a versão do Python do projeto.
- Use exclusivamente **Poetry** para dependências e ambiente virtual.
- Use **Ruff** como única ferramenta de lint e formatação.
- Use **pytest** para testes; mantenha-os em `tests/`.
- Mantenha o código-fonte em `src/projeto/`.
- Garanta cobertura mínima de **50%** sobre `src/projeto`.
- Use **MkDocs Material** para a documentação.

Não use `pip`, `venv`, `virtualenv`, `pipenv` nem `requirements.txt` como mecanismo principal de dependências ou ambientes. O Poetry cria, seleciona e administra a virtualenv; não a crie manualmente.

## Estrutura do projeto

```text
.
├── src/
│   └── projeto/
│       ├── __init__.py
│       └── ...
├── tests/
│   ├── __init__.py
│   └── test_*.py
├── docs/
├── mkdocs.yml
├── pyproject.toml
└── README.md
```

Use nomes de testes como `test_modulo.py` e funções como `test_comportamento_esperado()`. Um teste deve verificar comportamento observável, incluindo casos de erro relevantes.

## Configuração inicial

### 1. Python com pyenv

Instale o `pyenv` para o seu sistema operacional e, então, instale a versão de Python definida pelo projeto. A versão abaixo é um exemplo; ela deve coincidir com `requires-python` em `pyproject.toml`.

```bash
pyenv install 3.14.0
pyenv local 3.14.0
python --version
```

`pyenv local` cria o arquivo `.python-version` na raiz e fixa a versão somente para este repositório. Não use a instalação global do sistema como substituta. Ao atualizar a faixa de Python em `pyproject.toml`, atualize também `.python-version` e valide o projeto novamente.

### 2. Ambiente e dependências com Poetry

Instale o Poetry conforme o método oficial da plataforma e confirme a instalação:

```bash
poetry --version
poetry env use "$(pyenv which python)"
poetry install
```

O comando `poetry install` cria automaticamente a virtualenv do projeto e instala todas as dependências declaradas, inclusive as do grupo `dev`. Não ative nem crie uma virtualenv manualmente. Para ver onde ela está, use:

```bash
poetry env info
```

Em PowerShell, substitua a expansão de shell do segundo comando por:

```powershell
poetry env use (pyenv which python)
```

## Gerenciamento de dependências

`pyproject.toml` e `poetry.lock` são as fontes de verdade das dependências. Sempre versione ambos quando uma mudança de dependência alterar o lockfile.

| Objetivo | Comando |
| --- | --- |
| Instalar dependências bloqueadas | `poetry install` |
| Adicionar dependência de produção | `poetry add pacote` |
| Adicionar dependência de desenvolvimento | `poetry add --group dev pacote` |
| Remover dependência | `poetry remove pacote` |
| Atualizar dependências dentro das restrições | `poetry update` |
| Atualizar apenas um pacote | `poetry update pacote` |
| Executar comando na virtualenv | `poetry run comando` |
| Abrir shell na virtualenv (opcional) | `poetry shell` |
| Exibir detalhes do ambiente | `poetry env info` |

Exemplos:

```bash
poetry add httpx
poetry add --group dev pytest pytest-cov ruff mkdocs-material
poetry remove httpx
poetry run pytest
```

Não instale bibliotecas com `pip install`, mesmo dentro da virtualenv do Poetry. Para dependências opcionais ou conjuntos específicos, crie e documente grupos Poetry em vez de arquivos `requirements*.txt`.

## Qualidade de código: Ruff

O Ruff é a única ferramenta permitida para lint e formatação. Não adicione Black, isort, Flake8 ou ferramentas equivalentes.

Execute antes de enviar alterações:

```bash
poetry run ruff check .
poetry run ruff format --check .
```

Para corrigir automaticamente o que for possível:

```bash
poetry run ruff check . --fix
poetry run ruff format .
```

Organize imports pelo Ruff, use importações explícitas e remova código ou imports não usados. Ao aplicar correções automáticas, revise o diff antes do commit.

## Testes e cobertura

Use `pytest` para testes unitários. Toda nova funcionalidade, correção de defeito ou mudança de regra de negócio deve incluir ou atualizar testes em `tests/`.

```bash
poetry run pytest
poetry run pytest --cov=src/projeto --cov-report=term-missing
poetry run pytest --cov=src/projeto --cov-report=html
```

O primeiro relatório exibe no terminal as linhas ausentes. O segundo gera `htmlcov/index.html` para inspeção local. A cobertura deve ser de pelo menos 50% e incidir sobre `src/projeto`; o comando de testes falhará abaixo desse limiar.

## Documentação: MkDocs Material

A documentação técnica e de uso fica em `docs/` e é publicada com MkDocs Material. Instale-o somente pelo Poetry, normalmente no grupo `dev`:

```bash
poetry add --group dev mkdocs-material
```

Execute o servidor local enquanto escreve:

```bash
poetry run mkdocs serve
```

Gere o site estático para validação ou publicação:

```bash
poetry run mkdocs build --strict
```

`--strict` converte avisos de documentação em erro. Atualize a documentação quando uma mudança alterar instalação, configuração, APIs públicas, comportamento visível, exemplos ou decisões relevantes.

## Fluxo de desenvolvimento

1. Configure o interpretador com `pyenv local <versão>`.
2. Aponte o Poetry para o Python do pyenv e execute `poetry install`.
3. Crie ou atualize dependências exclusivamente com comandos Poetry.
4. Desenvolva em `src/projeto/`, com responsabilidades claras e mudanças pequenas.
5. Crie ou atualize os testes correspondentes em `tests/`.
6. Execute `poetry run ruff check . --fix` e `poetry run ruff format .`.
7. Execute `poetry run pytest` e confirme cobertura mínima de 50%.
8. Atualize os arquivos em `docs/` e valide com `poetry run mkdocs build --strict`.
9. Revise o diff, inclua `poetry.lock` quando aplicável e abra o Pull Request com contexto, testes executados e impacto documentado.

## Boas práticas de implementação

- Use type hints em parâmetros, retornos e atributos públicos; prefira tipos específicos a `Any`.
- Escreva funções pequenas, coesas e com uma responsabilidade bem definida.
- Separe domínio, infraestrutura, interfaces e orquestração para evitar acoplamento indevido.
- Prefira código simples, nomes claros e fluxo explícito a abstrações prematuras.
- Mantenha imports organizados e o projeto sem erros de Ruff.
- Não introduza nova funcionalidade sem testes adequados.
- Mantenha a documentação atualizada junto com o código, na mesma alteração quando possível.

## Configuração recomendada

### `pyproject.toml`

O trecho abaixo é a base recomendada. Ajuste `version` e a versão do Python somente de forma coordenada com `.python-version`.

```toml
[project]
name = "projeto"
version = "0.1.0"
description = ""
readme = "README.md"
requires-python = ">=3.14,<3.15"
dependencies = []

[tool.poetry]
packages = [{ include = "projeto", from = "src" }]

[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
pytest-cov = "^6.0"
ruff = "^0.12"
mkdocs-material = "^9.0"

[tool.ruff]
target-version = "py314"
line-length = 100
src = ["src"]

[tool.ruff.lint]
select = ["E", "F", "I", "UP", "B", "SIM"]

[tool.ruff.format]
quote-style = "double"
indent-style = "space"
line-ending = "auto"

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers --cov=src/projeto --cov-report=term-missing --cov-fail-under=50"

[tool.coverage.run]
branch = true
source = ["src/projeto"]

[tool.coverage.report]
show_missing = true
skip_covered = false

[build-system]
requires = ["poetry-core>=2.0.0,<3.0.0"]
build-backend = "poetry.core.masonry.api"
```

### `mkdocs.yml`

```yaml
site_name: Projeto
site_description: Documentação oficial do Projeto
repo_name: organizacao/projeto
theme:
  name: material
  language: pt
  features:
    - navigation.tabs
    - navigation.sections
    - content.code.copy
markdown_extensions:
  - admonition
  - pymdownx.highlight:
      anchor_linenums: true
  - pymdownx.superfences
nav:
  - Início: index.md
  - Guia de desenvolvimento: desenvolvimento.md
```

Crie os arquivos indicados em `nav` dentro de `docs/`. Antes de abrir um Pull Request, confirme que os comandos de Ruff, pytest/cobertura e MkDocs passam sem erros.
