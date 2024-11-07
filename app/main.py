from dotenv import load_dotenv
from fastapi import FastAPI

from app.indexing import URLContentIndexer
from app.api.endpoints import router as api_router
from app.utils.log_config import logger, setup_logging

# Set up logging configuration
setup_logging()

app = FastAPI()

# Load environment variables from .env file
load_dotenv()


# Include the API router
app.include_router(api_router, prefix="/api/v1")


# Initialize URLContentIndexer and store it in the application's state
app.state.url_content_indexer = URLContentIndexer()


@app.get("/")
def read_root():
    logger.debug("Root endpoint accessed.")
    return {"message": "Welcome to the RAG API!"}
