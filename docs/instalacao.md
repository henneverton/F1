# Instalação

O projeto usa exclusivamente **pyenv** para a versão do Python e **Poetry**
para dependências e ambiente virtual. Não use `pip`, `venv`, `virtualenv`
nem `requirements.txt`.

## 1. Python com pyenv

```bash
pyenv install 3.14.5
pyenv local 3.14.5
python --version
```

`pyenv local` cria o ficheiro `.python-version` na raiz do repositório,
fixando a versão apenas para este projeto.

## 2. Ambiente e dependências com Poetry

```bash
poetry --version
poetry env use "$(pyenv which python)"
poetry install
```

`poetry install` cria a virtualenv automaticamente e instala as dependências
de produção (`httpx`, `streamlit`) e de desenvolvimento (`ruff`, `pytest`,
`pytest-cov`, `mkdocs-material`). Não ative nem crie a virtualenv
manualmente.

Em PowerShell, use:

```powershell
poetry env use (pyenv which python)
```

## 3. Executar o dashboard

```bash
poetry run streamlit run src/f1/app.py
```

O Streamlit abre o dashboard no navegador (por omissão em
`http://localhost:8501`). Não é necessária nenhuma chave de API: os dados
históricos da OpenF1 são gratuitos e não exigem autenticação.
