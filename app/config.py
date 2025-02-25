import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
WEAVIATE_URL = os.getenv("WEAVIATE_URL", "http://localhost:8080")
WEAVIATE_API_KEY = os.getenv("WEAVIATE_API_KEY")
AZURE_VISION_KEY = os.getenv('AZURE_VISION_KEY')
AZURE_VISION_ENDPOINT=os.getenv('AZURE_VISION_ENDPOINT')

# Document Processing Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Weaviate Configuration
WEAVIATE_CLASS_NAME = "Document"
WEAVIATE_SCHEMA = {
    "class": WEAVIATE_CLASS_NAME,
    "vectorizer": "text2vec-openai",
    "moduleConfig": {
        "text2vec-openai": {
            "model": "ada",
            "modelVersion": "002",
            "type": "text"
        }
    },
    "properties": [
        {
            "name": "chunkId",
            "dataType": ["text"],
            "description": "The ID of this chunk"
        },
        {
            "name": "chunkDataType",
            "dataType": ["text"],
            "description": "The data type of this chunk"
        },
        {
            "name": "chunkData",
            "dataType": ["text"],
            "description": "The data content of this chunk"
        },
        {
            "name": "fileType",
            "dataType": ["text"],
            "description": "The type of the file"
        }
    ]
}

# Supported document types
SUPPORTED_DOCUMENT_TYPES = {
    "pdf": "application/pdf",
    "docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "json": "application/json",
    "txt": "text/plain"
} 