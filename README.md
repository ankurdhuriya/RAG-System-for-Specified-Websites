# RAG-System-for-Specified-Websites

A Retrieval Augmented Generation (RAG) system designed to answer user queries based on information from specific websites. This system utilizes a vector database to efficiently store and retrieve relevant information, enabling accurate and informative responses.

## Requirements

To run this project, you need to have Python version **3.9** installed. You can manage your dependencies using the provided `requirements.txt` file.

## Installation

1. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

2. Install Requirements:
   ```bash
   pip install -r requirements.txt
   ```

## API Endpoints

*POST `api/v1/index`*

*INPUT*
```json
{
    "url": [
        "https://lilianweng.github.io/posts/2023-01-27-the-transformer-family-v2/",
        ...
         // url need to by httpurl format not any string
    ]
}
```

*OUTPUT*
```json
{
    "status": "success",
    "indexed_url": [
        "https://lilianweng.github.io/posts/2023-01-27-the-transformer-family-v2".
        ... 
    ],
    "failed_url": []
}
```

*POST `api/v1/chat`*

*INPUT* 
```json
{
  "messages": [
    {
      "content": "Hello, how are you?",
      "role": "user" //role could be user or assistant only
    },
    {
      "content": "I'm doing well, thank you. How can I help you today?",
      "role": "assistant"
    },
    ....
  ]
}

*OUTPUT*

```json
{
    "responses": [
      "answer": {
         "content": "",
         "role": "" // assistant
      },
      "citations": [], // list of urls
    ]
}
```

## Deployment Overview

# Procfile Configuration
The Procfile is a crucial component for deploying your FastAPI application on platforms like Railway.app. It specifies the commands that are executed by the application server. For your FastAPI application, the Procfile should contain the following line:

```bash
web: uvicorn app.main:app --host=0.0.0.0 --port=${PORT:-8000}
```

## Deployment on Railway App
Railway.app is a cloud platform that simplifies the deployment process for applications, allowing developers to focus on building rather than managing infrastructure. 

## Key Features of  Application

# API Key Authentication:
* The application uses API key authentication to secure its endpoints, ensuring that only authorized users can access sensitive functionalities.
* This is implemented using FastAPI's dependency injection system, where API keys are checked against a predefined list.
  
# Integration with Groq API:
* The application utilizes the Llama model (llama-3.1-8b-instant) from Groq API for generating responses based on user queries.
* This model provides advanced natural language processing capabilities, enhancing the application's ability to understand and respond to user requests.

# Pinecone Vector Database
* The application leverages Pinecone as a vector database to store and retrieve relevant information efficiently.
* This setup enables fast indexing and querying of data, which is crucial for providing accurate and timely responses to user queries.

# Settings Configuration
The configuration settings are managed through a Settings class, allowing easy adjustments for project name, version, vector database index, embedding model, and LLM model.

```python
class Settings:
    PROJECT_NAME: str = "RAG FastAPI Application"
    VERSION: str = "1.0.0"
    VECTOR_DB_INDEX = "rag-demo-application"
    EMBEDDING_MODEL = "sentence-transformers/all-mpnet-base-v2"
    LLM = "llama-3.1-8b-instant"

settings = Settings()
```
