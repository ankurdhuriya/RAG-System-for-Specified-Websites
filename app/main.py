from dotenv import load_dotenv
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.indexing import URLContentIndexer
from app.api.endpoints import router as api_router
from app.utils.log_config import logger, setup_logging

# Set up logging configuration
setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup event triggered.")
    # Load environment variables from .env file
    load_dotenv()
    
    # Initialize URLContentIndexer and store it in the application's state
    app.state.url_content_indexer = URLContentIndexer()
    
    yield  # This yields control back to FastAPI during the lifespan of the app

    logger.info("Application shutdown event triggered.")
    # Add any cleanup tasks here, e.g., closing database connections, releasing resources

app = FastAPI(lifespan=lifespan)

# Include the API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def read_root():
    logger.debug("Root endpoint accessed.")
    return {"message": "Welcome to the RAG API!"}