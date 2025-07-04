

BASE_USER_QUERIES = [
    "Pease list all the current senior squad members for the Manchester United men's team",
    "Can you provide the full list of current senior players for Manchester United men's team?",
    "Please show me the current Manchester United men's first team squad.",
    "I'd like to see all the players currently in the senior squad for Manchester City men's side.",
    "List the current roster of senior players for Liverpool men's football team.",
    "Who are the current members of Manchester United's men's senior squad?"
]

IRRELEVANT_USER_QUERIES = [
    "What is the weather in Warsaw?",
    "What is the population of Warsaw?",
    "How are you?",
    "What is the capital of France?",
    "My name is John."
]

NOT_PREMIER_LEAGUE_TEAMS_QUERIES = [
    "Please tell me the squad of the Chico Bulls",
    "Can you provide the full list of current senior players for Barcelona men's team?",
    "List the current roster of senior players for Paris Saint-Germain men's football team.",
    "List the current roster of senior players for Real Madrid men's football team."
]

PRECISE_USER_QUERIES = [
    "What are the players born after 2000 of the Manchester United?",
    "What are defenders of the Manchester United?",
]

UNCLEAR_TEAMS_QUERIES = [
    "What is the squad of Manchester?",
    "What is the squad of Man?",
    "What is the squad of Crystal?",
    "What is the squad of Man City?",
    "What is the squad of Brighton?",
    "What is the squad of Manshesterr?"
]

DIFFRENT_LANGUAGES_QUERIES = [
    "Jaki jest skład Manchester United?",
    "Qual è il nome del Manchester United?",
    "Який склад Манчестер Юнайтед?"
]

EVALUATION_QUERIES = BASE_USER_QUERIES + IRRELEVANT_USER_QUERIES + NOT_PREMIER_LEAGUE_TEAMS_QUERIES + PRECISE_USER_QUERIES + UNCLEAR_TEAMS_QUERIES + DIFFRENT_LANGUAGES_QUERIES