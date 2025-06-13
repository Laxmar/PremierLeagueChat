import os

from pydantic import BaseModel, SecretStr
import yaml
from loguru import logger

DEFUALT_CONFIG_PATH = "config.yaml"

class Configuration(BaseModel):
    model_name: str = "gpt-4.1"
    logging_level: str = "info"
    langraph_debug: bool = False
    OPENAI_API_KEY: SecretStr
    
    def model_post_init(self, __context):
        os.environ["OPENAI_API_KEY"] = self.OPENAI_API_KEY.get_secret_value()
    
    @classmethod
    def load(cls, path: str = DEFUALT_CONFIG_PATH) -> "Configuration":
        """load configuration from yaml file"""
        logger.debug(f'Loading configuration from {path}')
        with open(path, "r") as f:
            return cls(**yaml.safe_load(f))
    
