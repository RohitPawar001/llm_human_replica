from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict
from zenml.client import Client
from zenml.exceptions import EntityExistsError 

class Settings(BaseSettings):
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    
    # required even for the local deployment
    
    # openAi api
    OPENAI_MODEL_ID : str | None = "gpt-4o-mini"
    OPENAI_API_KEY : str | None = None
    
    #HuggingFace API
    HUGGINGFACE_ACCESS_TOKEN : str | None = None
    
    # CometMl 
    COMET_API_KEY : str | None = None
    COMET_PROJECT : str | None = None
    
    @property
    def OPENAI_MAX_TOKEN_WINDOW(self) -> int:
        official_max_token_window = {
            "gpt_3.5-turbo": 16358,
            "gpt-3.5-turbo": 16385,
            "gpt-4-turbo": 128000,
            "gpt-4o": 128000,
            "gpt-4o-mini": 128000,
        }.get(self.OPENAI_MODEL_ID, 128000)
        
        max_token_window = int(official_max_token_window * 0.90)
        
        return max_token_window
    
    @classmethod
    def load_settings(cls) -> "Settings":
        try:
            logger.info("loading settings from the Zenml secrete store.")
            
            settings_secrets = Client().get_secret("settings")
            settings = Settings(**settings_secrets.secret_values)
            
        except (RuntimeError, KeyError):
            logger.warning(
                "Failed to load settings from the zenml secrete store."
            )
            settings = Settings()
            
        return settings
    
    def export(self) -> None:
        env_vars = self.model_dump()
        for key, value in env_vars.items():
            env_vars[key] = str(value)
            
        client = Client()
        
        try:
            client.create_secret(name="settings", values=env_vars)
        except EntityExistsError:
            logger.warning(
                "secret 'settings' already exists. Delete it manually by running 'zenml secret delete settings', before trying to recreate it."
            )


if __name__ == "__main__":
    settings = Settings.load_settings()
else:
    settings = Settings.load_settings()
    
    