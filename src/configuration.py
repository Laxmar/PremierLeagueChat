import os

from pydantic import BaseModel, SecretStr
import yaml
from loguru import logger

DEFUALT_CONFIG_PATH = "config.yaml"

class Configuration(BaseModel):
    """Application configuration Check example_config.yaml"""
    
    MODEL_NAME: str = "gpt-4.1"
    """https://platform.openai.com/docs/models/overview"""
    LOGGING_LEVEL: str = "info"
    """ avaible levels: trace, debug, info, success, warning, error, critical"""
    LANGRAPH_DEBUG: bool = False
    """ enable langgraph debug"""
    
    OPENAI_API_KEY: SecretStr
    """https://platform.openai.com/"""
    THE_SPORT_API_KEY: SecretStr
    """https://www.thesportsdb.com/"""
    
    def model_post_init(self, __context):
        os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY.get_secret_value()
    
    @classmethod
    def load(cls, path: str = DEFUALT_CONFIG_PATH) -> "Configuration":
        """load configuration from yaml file
        
        Args:
            path: path to the configuration file
        
        Returns:
            Configuration: loaded configuration
        """
        logger.debug(f'Loading configuration from {path}')
        
        try:
            with open(path, "r") as f:
                return cls(**yaml.safe_load(f))
        except Exception as e:
            logger.warning(f"Failed to load config from {path}: {e}. Loading from environment variables.")
            env_vars = {
                "MODEL_NAME": os.getenv("MODEL_NAME", "gpt-4.1"),
                "LOGGING_LEVEL": os.getenv("LOGGING_LEVEL", "info"),
                "LANGRAPH_DEBUG": os.getenv("LANGRAPH_DEBUG", "False") in ("True", "true", "1"),
                "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
                "THE_SPORT_API_KEY": os.getenv("THE_SPORT_API_KEY"),
            }
            return cls(**env_vars)
    
