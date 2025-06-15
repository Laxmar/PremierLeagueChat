import os

from pydantic import BaseModel, SecretStr
import yaml
from loguru import logger

DEFUALT_CONFIG_PATH = "config.yaml"

class Configuration(BaseModel):
    model_name: str = "gpt-4.1"
    """https://platform.openai.com/docs/models/overview"""
    logging_level: str = "info"
    """ avaible levels: trace, debug, info, success, warning, error, critical"""
    langraph_debug: bool = False
    """ enable langgraph debug"""
    
    OPENAI_API_KEY: SecretStr
    """https://platform.openai.com/"""
    THE_SPORT_API_KEY: SecretStr
    """https://www.thesportsdb.com/"""
    
    def model_post_init(self, __context):
        os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY.get_secret_value()
    
    @classmethod
    def load(cls, path: str = DEFUALT_CONFIG_PATH) -> "Configuration":
        """load configuration from yaml file"""
        logger.debug(f'Loading configuration from {path}')
        with open(path, "r") as f:
            return cls(**yaml.safe_load(f))
    
