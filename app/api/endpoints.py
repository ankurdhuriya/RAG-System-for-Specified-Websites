from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse

from app.api.models import ChatRequest, ChatResponse, IndexRequest, IndexResponse
from app.utils.log_config import logger

router = APIRouter()


@router.post("/index", response_model=IndexResponse)
async def index_endpoint(
    app_request: Request, request_model: IndexRequest
) -> JSONResponse:
    """
    Indexes the provided URLs.

    This endpoint takes a list of URLs in the request body and attempts to index their content
    for later retrieval. It returns a JSON response with the status of the indexing operation,
    including a list of successfully indexed URLs and any URLs that failed to be indexed.

    Args:
        app_request: The FastAPI request object.
        request_model: An IndexRequest object containing the list of URLs to be indexed.

    Returns:
        A JSONResponse object with the indexing status and details.
    """

    try:
        logger.info(f"Request Body: {request_model.dict()}")
        (
            indexed_url,
            failed_url,
        ) = await app_request.app.state.url_content_indexer.index_urls(
            request_model.url
        )

        logger.info(f"Indexed URLs: {indexed_url}")
        logger.warning(f"Failed URLs: {failed_url}")  # Log failed URLs as warnings

        logger.info(
            f"Response: {({'status': 'success' if indexed_url else 'failed', 'indexed_url': indexed_url, 'failed_url': failed_url})}"
        )

        return JSONResponse(
            {
                "status": "success" if indexed_url else "failed",
                "indexed_url": indexed_url,
                "failed_url": failed_url,
            }
        )
    except Exception as e:
        logger.error(f"Error during indexing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    app_request: Request, request_model: ChatRequest
) -> JSONResponse:
    """
    Processes a chat request and generates a response.

    This endpoint takes a list of messages in the request body and attempts to generate a
    response based on the message content. It returns a JSON response with a list of potential
    answers and their corresponding citations.

    Args:
        app_request: The FastAPI request object.
        request_model: A ChatRequest object containing the list of messages in the chat.

    Returns:
        A JSONResponse object with the generated responses and citations.
    """

    try:
        logger.info(f"Request Body: {request_model.dict()}")
        answer_content, citations = await app_request.app.state.chat.generate_response(
            request_model.dict().get("messages")
        )

        logger.info(
            f"Response: {({'response': [{'answer': {'content': answer_content, 'role': 'assistant'}, 'citation': list(citations)}]})}"
        )

        return JSONResponse(
            {
                "response": [
                    {
                        "answer": {"content": answer_content, "role": "assistant"},
                        "citation": list(citations),
                    }
                ]
            }
        )
    except Exception as e:
        logger.error(f"Error during chat processing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
