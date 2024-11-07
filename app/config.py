class Settings:
    PROJECT_NAME: str = "RAG FastAPI Application"
    VERSION: str = "1.0.0"
    VECTOR_DB_INDEX = "rag-demo-application"
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    LLM = "llama-3.1-8b-instant"


settings = Settings()
