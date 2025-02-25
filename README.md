# RinggAI : Backend Engineering Take-Home Assignment

This is a Retrieval Augmented Generation (RAG) system built with FastAPI and Weaviate. The system supports document ingestion, embedding generation, and question-answering capabilities.

## Features

- Document ingestion support for multiple formats:
  - PDF
  - DOCX
  - JSON
  - TXT
- Automated embedding generation using OpenAI's text-embedding model
- Document storage and retrieval using Weaviate vector database
- RESTful API endpoints for document management and querying
- Performance optimizations including document chunking and precomputed embeddings

## Prerequisites

- Python 3.8+
- Weaviate instance
- OpenAI API key

## Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd rag-system
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file with the following variables:
```
OPENAI_API_KEY=your_openai_api_key
WEAVIATE_URL=your_weaviate_url
WEAVIATE_API_KEY=your_weaviate_key
AZURE_VISION_KEY=
AZURE_VISION_ENDPOINT=
```

5. Start the application:
```bash
uvicorn app.main:app --reload
```

## API Endpoints

### Document Management

- `POST /documents/upload`
  - Upload a new document
  - Supports PDF, DOCX, JSON, and TXT formats
  - Automatically generates and stores embeddings

### Querying

- `POST /query`
  - Query against specific documents
  - Returns relevant text snippets and metadata

## Project Structure

```
.
├── app/
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── models/              # Pydantic models
│   ├── services/            # Business logic
│   │   ├── document.py      # Document processing
│   │   ├── embedding.py     # Embedding generation
│   │   └── weaviate.py      # Vector database operations
│   └── utils/               # Utility functions
├── requirements.txt         # Project dependencies
└── README.md               # Project documentation
```

## Design Choices

- FastAPI for high-performance async API development
- Weaviate as the vector database for efficient similarity search
- OpenAI's text-embedding model for high-quality embeddings
- Document chunking for optimal retrieval performance
- Modular architecture for easy maintenance and scalability
