import hashlib
import time
import urllib.parse
from urllib.parse import urlparse

from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import UnstructuredURLLoader
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone, ServerlessSpec

from app.config import settings
from app.utils.log_config import logger

index_name = settings.VECTOR_DB_INDEX


def create_index() -> None:
    """Creates a Pinecone index if it doesn't exist."""
    pc = Pinecone()
    existing_indexes = [index_info["name"] for index_info in pc.list_indexes()]

    if index_name not in existing_indexes:
        logger.info(f"Creating Pinecone index: {index_name}")
        pc.create_index(
            name=index_name,
            dimension=768,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        while not pc.describe_index(index_name).status["ready"]:
            time.sleep(2)
        logger.info(f"Pinecone index {index_name} created successfully.")

    _ = pc.Index(index_name)


class URLContentIndexer:
    """Indexes content from given URLs into a Pinecone vector store."""

    def __init__(self) -> None:
        create_index()  # Create the Pinecone index if it doesn't exist
        self.text_splitter = CharacterTextSplitter(
            separator="\n", chunk_size=1000, chunk_overlap=200
        )
        self.embedding = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.vectorstore = PineconeVectorStore(
            index_name=settings.VECTOR_DB_INDEX, embedding=self.embedding
        )
        self.llm = ChatGroq(model=settings.LLM, temperature=0, max_retries=3)

    def index_urls(self, urls: list[str]):
        """Indexes the given URLs into the vector store.

        Args:
            urls: A list of URLs to index.
        """
        urls = [str(u) for u in urls]  # Ensure URLs are strings

        indexed_url = []
        failed_url = []

        for url in urls:
            try:
                url = URLContentIndexer.normalize_url(url)
                loader = UnstructuredURLLoader(urls=[url])
                data = loader.load()  # Load data from URLs

                text_splitter = CharacterTextSplitter(
                    separator="\n", chunk_size=500, chunk_overlap=100
                )
                text_chunks = text_splitter.split_documents(
                    data
                )  # Split data into chunks
                ids = [
                    URLContentIndexer.get_unique_id(idx, url)
                    for idx, _ in enumerate(text_chunks)
                ]
                ids = self.vectorstore.add_documents(documents=text_chunks, ids=ids)
                indexed_url.append(url)
                logger.info(f"URL indexed successfully: {url}")
            except Exception as e:
                failed_url.append(url)
                logger.warning(f"Failed to index URL: {url}, Error: {str(e)}")

        if failed_url:
            logger.warning(f"Failed to index the following URLs: {failed_url}")

    @staticmethod
    def get_unique_id(index, url):
        """Generates a unique ID for a document based on its index and URL."""
        return f"{index}_{hashlib.sha256(url.encode()).hexdigest()}"

    @staticmethod
    def normalize_url(url):
        """Normalizes a URL to remove potential duplicates."""

        parsed = urlparse(url)

        # Normalize scheme and hostname to lowercase
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()

        # Remove trailing slash from path
        path = parsed.path.rstrip("/")

        # Sort query parameters alphabetically
        query = urllib.parse.urlencode(
            sorted(urllib.parse.parse_qsl(parsed.query)), doseq=True
        )

        # Reconstruct the URL
        return urllib.parse.urlunparse(
            (scheme, netloc, path, parsed.params, query, parsed.fragment)
        )
