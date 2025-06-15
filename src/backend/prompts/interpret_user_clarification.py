
from langchain.prompts import PromptTemplate

INTERPRET_USER_CLARIFICATION_PROMPT = PromptTemplate.from_template(
"""
You are a football assistant specialized in the Premier League.

To clarify, you previously asked (clarification request):
{clarification_request}

The user responded with (clarification response):
{clarification_response}

Your task is:
- Analyze the above information and determine the most likely Premier League team the user is referring to.
- Use only the data from the clarification request and the clarification response.
- Do not use any additional information
- Do not change the team name and formatting from clarification request

Your output should be:
- Return only the full official Premier League team name, if you can confidently identify it.
- If you are unsure or the team does not exist in the Premier League, return: UNKNOWN.

Only return the team name or UNKNOWN, and nothing else.
"""
)