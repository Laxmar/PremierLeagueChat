
from datetime import date
from langchain.prompts import PromptTemplate

from src.backend.squad import ALL_PLAYER_GROUPS, PlayersGroup, Squad

def build_formulate_answer_prompt(squad: Squad, user_question: str) -> str:
    """Builds a prompt for the model to formulate an answer to the user question based on the squad data.
    Args:
        squad (Squad): The squad data.
        user_question (str): The user question.
    Returns:
        str: The prompt for the model.
    """
    markdown_parts = ["# Squad\n"]
    for section in ALL_PLAYER_GROUPS:
        if section in squad.get_player_group():
            markdown_parts.append(f"## {section}")
            for player in squad.get_player_group()[section]:
                if section == PlayersGroup.Manager:
                    markdown_parts.append(f"- {player.name} ({player.date_of_birth})")
                else:
                    markdown_parts.append(f"- {player.name} ({player.date_of_birth}) - {player.position}")

    squad_markdown = "\n".join(markdown_parts)

    prompt_template = PromptTemplate.from_template("""
    You are a football squad expert assistant.

    You have access to the following squad:

    {squad_markdown}

    When answering questions:
    - Use only the data from the squad.
    - If asked bout the squad present the players names, positions and birthdates.
    - If the data is not present, politely say "I don't have information about that."
    - If asked for positions, group players by positions.
    - If asked for ages, calculate the age based on today's date ({today}).
    - If asked for youngest/oldest players, compare birthdates.
    - If asked for number of players, give precise counts.
    - Be precise and concise.

    Now answer the following user question:

    {user_question}
    """)

    prompt = prompt_template.format(
        squad_markdown=squad_markdown,
        user_question=user_question,
        today=date.today().isoformat()
    )

    return prompt