from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    # LLM configuration
    openai_api_key: str
    openai_base_url: str = "https://api.scitely.com/v1"
    openai_model: str = "qwen3-32b"

    # embeddings
    openai_embedding_model: str = "text-embedding-3-small"

    # storage
    data_dir: str = "data"

    # indexing limits
    index_max_files: int = 4000
    index_max_file_bytes: int = 400000

    # chunking
    chunk_size_chars: int = 1400
    chunk_overlap_chars: int = 200

    class Config:
        env_file = ".env"


settings = Settings()