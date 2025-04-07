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

    # Mongodb database
    DATABASE_HOST: str = "mongodb+srv://rppawar491:5jE80ODBsHO9ukx6@cluster0.avcipcb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DATABASE_NAME:str = "twin"

    # Qdrant vector database
    USE_QDRANT_CLOUD: bool = False
    QDRANT_DATABASE_HOST: str = "localhost"
    QDRANT_DATABASE_PORT: int = 6333
    QDRANT_CLOUD_URL: str = "str"
    QDRANT_APIKEY: str | None = None

    # AWS Authentication
    AWS_REGION: str = "eu-central-1"
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None

    # AWS SageMaker
    HF_MODEL_ID: str = "mlabonne/TwinLlama-3.1-8B-DPO"
    GPU_INSTANCE_TYPE: str = "ml.g5.2xlarge"
    SM_NUM_GPUS: int = 1
    MAX_INPUT_LENGTH: int = 2048
    MAX_TOTAL_TOKENS: int = 4096
    MAX_BATCH_TOTAL_TOKENS: int = 4096
    COPIES: int = 1  # Number of replicas
    GPUS: int = 1  # Number of GPUs
    CPUS: int = 2  # Number of CPU cores

    SAGEMAKER_ENDPOINT_CONFIG_INFERENCE: str = "twin"
    SAGEMAKER_ENDPOINT_INFERENCE: str = "twin"
    TEMPERATURE_INFERENCE: float = 0.01
    TOP_P_INFERENCE: float = 0.9
    MAX_NEW_TOKENS_INFERENCE: int = 150

    # RAG
    TEXT_EMBEDDING_MODEL_ID: str = "sentence-transformers/all-MiniLM-L6-v2"
    RERANKING_CROSS_ENCODER_MODEL_ID: str = "cross-encoder/ms-marco-MiniLM-L-4-v2"
    RAG_MODEL_DEVICE: str = "cpu"

    # LinkedIn Credentials
    LINKEDIN_USERNAME: str | None = None
    LINKEDIN_PASSWORD: str | None = None

    
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



settings = Settings.load_settings()

    
    