import enum

from collections import defaultdict
from datetime import date
from src.backend.squad import Squad

class PlayersGroup(enum.StrEnum):
    Goalkeepers = "Goalkeepers"
    Manager = "Manager"
    Defenders = "Defenders"
    Midfielders = "Midfielders"
    Forwards = "Forwards"
    Others = "Others"

ALL_PLAYER_GROUPS = list(PlayersGroup)

def build_formulate_answer_prompt(squad: Squad, user_question: str) -> str:
    """Builds a prompt for the model to formulate an answer to the user question based on the squad data.
    Args:
        squad (Squad): The squad data.
        user_question (str): The user question.
    Returns:
        str: The prompt for the model.
    """

    postion_to_player_group = {
        "Goalkeeper": PlayersGroup.Goalkeepers,
        "Manager": PlayersGroup.Manager,
        "Defender": PlayersGroup.Defenders,
        "Centre-Back": PlayersGroup.Defenders,
        "Left-Back": PlayersGroup.Defenders,
        "Right-Back": PlayersGroup.Defenders,
        "Attacking Midfield": PlayersGroup.Midfielders,
        "Central Midfield": PlayersGroup.Midfielders,
        "Defensive Midfield": PlayersGroup.Midfielders,
        "Centre-Forward": PlayersGroup.Forwards,
        "Right Winger": PlayersGroup.Forwards,
        "Left Wing": PlayersGroup.Forwards,
    }

    grouped = defaultdict(list)
    for player in squad.players:
        group = postion_to_player_group.get(player.position, PlayersGroup.Others)
        grouped[group].append(player)

    markdown_parts = ["# Squad\n"]
    for section in ALL_PLAYER_GROUPS:
        if section in grouped:
            markdown_parts.append(f"## {section}")
            for player in grouped[section]:
                if section == PlayersGroup.Manager:
                    markdown_parts.append(f"- {player.name} ({player.date_of_birth})")
                else:
                    markdown_parts.append(f"- {player.name} ({player.date_of_birth}) - {player.position}")

    squad_markdown = "\n".join(markdown_parts)

    prompt_template = """
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
    """

    prompt = prompt_template.format(
        squad_markdown=squad_markdown,
        user_question=user_question,
        today=date.today().isoformat()
    )

    return prompt