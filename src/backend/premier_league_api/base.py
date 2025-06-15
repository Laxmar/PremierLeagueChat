from abc import ABC, abstractmethod
from src.backend.squad import Squad

class IPremierLeagueApi(ABC):
    
    @abstractmethod
    def get_teams(self) -> list[str]:
        """ Returns list of Premier League team names for season 2025/2026
        
        Returns:
            list[str]: List of Premier League team names
        Example:
            ["manchester united", "manchester city", "liverpool", ...]
        """
        pass
    
    @abstractmethod
    def get_team_squad(self, team_name: str) -> Squad:
        """ Returns squad of a team
        
        Args:
            team_name (str): Name of the team, lowercase with spaces
                Example: "manchester united"
        
        Returns:
            Squad: Squad of the team
        """
        pass