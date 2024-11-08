from typing import List, Tuple

from langchain import hub
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_pinecone import PineconeVectorStore

from app.config import settings
from app.prompts import contextualize_q_system_prompt
from app.utils.log_config import logger


class Chat:
    def __init__(self):
        self.llm = ChatGroq(model=settings.LLM, temperature=0, max_retries=3)
        embedding = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
        self.vector_store = PineconeVectorStore(
            index_name=settings.VECTOR_DB_INDEX, embedding=embedding
        )
        self.rag_prompt = hub.pull("rlm/rag-prompt")
        self.single_ques_prompt = PromptTemplate(template=contextualize_q_system_prompt)

    async def formulate_single_question(self, messages: List[Tuple[str, str]]) -> str:
        """
        Formulates a standalone question based on the provided chat history.

        Args:
            messages (list): A list of message tuples containing user and assistant messages.

        Returns:
            str: The reformulated question or an error message if something goes wrong.
        """
        try:
            chain = self.single_ques_prompt | self.llm | StrOutputParser()
            result = await chain.ainvoke({"chat_history": messages})
            return result
        except Exception as e:
            logger.error(f"Error in formulate_single_question: {e}")
            raise Exception

    @staticmethod
    def process_documents(docs) -> Tuple[str, set]:
        relevant_content = "\n\n".join(doc.page_content for doc in docs)
        citations = set()
        for doc in docs:
            citations.add(doc.metadata.get("source"))
        return relevant_content, citations

    async def generate_response(self, messages: List[Tuple[str, str]]):
        """
        Generates a response based on the provided chat history.

        Args:
            messages (List[Tuple[str, str]]): A list of message tuples containing user and assistant messages.

        Returns:
            str: The generated response or an error message if something goes wrong.
        """
        try:
            # Step 1: Formulate a single question from the chat history
            question = await self.formulate_single_question(messages)

            # Step 2: Retrieve context
            docs = self.vector_store.similarity_search(question, k=3)

            context, citations = Chat.process_documents(docs)

            chain = self.rag_prompt | self.llm | StrOutputParser()

            # Step 3: Invoke the RAG chain with the formulated question
            result = await chain.ainvoke({"context": context, "question": question})

            return result, citations
        except Exception as e:
            # Handle exceptions and log errors for debugging
            logger.error(f"Error in generate_response: {e}")
            raise e
