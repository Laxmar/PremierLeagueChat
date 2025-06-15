# Premier League Chat

This is a simple chatbot that can answer questions regarding Premier League teams squads.

# Requirements

- Python 3.12
- Poetry
- OPENAI_API_KEY with access to GPT-4.1

# Setup

```bash
poetry install
```
- copy example_config.yaml to config.yaml
- fill OPENAI_API_KEY with your OpenAI API key
- fill THE_SPORT_API_KEY with your TheSportDB API key (https://www.thesportsdb.com/)


# Usage

```bash
eval $(poetry env activate)
```
or 
```bash
source activate_env.fish
```

## Run prototype

```bash
streamlit run src/prototype.py
```

## Run the use cases test

```bash
python -m tests.test_use_cases
```

# Development & Contribution

## Add package
```bash
poetry add <package_name>
```

## Tech stack

- Python 3.12
- Poetry
- Pytest
- Pyright
- Langchain
- Langgraph
- Streamlit
- Loguru
- OpenAI API
- [TheSportDB API](https://www.thesportsdb.com/)


## Docs - TODO

- in docs/ directory 