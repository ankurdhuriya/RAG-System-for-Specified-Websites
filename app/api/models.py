from typing import List, Literal, Optional

from pydantic import BaseModel, HttpUrl


class IndexRequest(BaseModel):
    """Represents a request to index URLs."""
    url: List[HttpUrl]


class IndexResponse(BaseModel):
    """Represents the response to an index request."""
    status: str
    indexed_url: List[str]
    failed_url: Optional[List[str]]


class Message(BaseModel):
    """Represents a single message in a chat."""
    content: str
    role: Literal["user", "assistant"]  # Should be either "user" or "assistant"


class ChatRequest(BaseModel):
    """Represents a chat request with a list of messages."""
    messages: List[Message]


class Answer(BaseModel):
    """Represents an answer to a query."""
    content: str
    role: Literal["user", "assistant"]


class Citation(BaseModel):
    """Represents a citation with a list of URLs."""
    url: List[HttpUrl]


class ChatResponse(BaseModel):
    """Represents a chat response with a list of answers and citations."""
    responses: List[dict[str, Answer, Citation]]