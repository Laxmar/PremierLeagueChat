# Premier League Chat

This is a simple chatbot that can answer questions regarding Premier League teams squads.

# Requirements

- Python 3.12
- Poetry
- OPENAI_API_KEY with access to GPT-4.1
- THE_SPORT_API_KEY with access to TheSportDB API

# Setup

```bash
poetry install
```
- copy example_config.yaml to config.yaml
- fill OPENAI_API_KEY with your OpenAI API key
- fill THE_SPORT_API_KEY with your TheSportDB API key (https://www.thesportsdb.com/)
- You can also set all environment variables for more check src/configuration.py 

# Usage

```bash
eval $(poetry env activate)
```
or 
```bash
source activate_env.fish
```

## Run app with frontend

```bash
streamlit run src/frontend/app.py
```

## Evaluation

```bash
python -m tests.evaluation
```

```bash
python -m test.evaluate_all_teams
```


# Development & Contribution

## Add package
```bash
poetry add <package_name>
```

## Tech stack

- Python 3.12
- Langgraph & Langchain
- Streamlit
- Poetry
- OpenAI API
- [TheSportDB API](https://www.thesportsdb.com/)
- Pytest
- Loguru
- Pyright (currently on IDE, and manually)
- Ruff (currently on IDE, and manually)


## Tasks Board

https://github.com/users/Laxmar/projects/1/views/1

## Docs 

Read the docs/Premier League Chat - Proof of Concept - Documentation.pdf for more information.

## Deployment

App is currently deployed using https://streamlit.io/cloud. Before the deployment, you need to set environment variables in the Streamlit Cloud console. The app is automatically deployed when you push to the main branch.