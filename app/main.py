from fastapi import FastAPI

from app.api.endpoints import router as api_router
from app.core.log_config import setup_logging, logger

# Set up logging configuration
setup_logging()

app = FastAPI()

# Include the API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def read_root():
    logger.debug("Root endpoint accessed.")
    return {"message": "Welcome to the RAG API!"}
