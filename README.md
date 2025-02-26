# RinggAI : Backend Engineering Take-Home Assignment

This is a Retrieval Augmented Generation (RAG) system built with FastAPI and Weaviate. The system supports document ingestion, embedding generation, and question-answering capabilities.

# Public URL : http://13.233.159.13:8000


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

4. Create a `app/.env` file with the following variables:
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

### API Doc

- `GET /doc`
  - Graphical User Interface (GUI) for viewing all endpoints and interactive testing

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
│   ├── main.py               # FastAPI application
│   ├── config.py             # Configuration settings
│   ├── models/               # Pydantic models
│   ├── services/             # Business logic
│   │   ├── document.py       # Document processing
|   |   ├── vision_service.py # Azure Image OCR Service
│   │   ├── embedding.py      # Embedding generation
│   │   └── weaviate.py       # Vector database operations
│   └── utils/                # Utility functions
├── requirements.txt          # Project dependencies
└── README.md                 # Project documentation
```

### Workflow Overview

1. **Document Upload & Processing**  
   - Users upload documents (PDF, DOC, etc.).  
   - The system reads the document part by part, identifying text and images separately.  

2. **OCR and Image Processing**  
   - If the document contains images, Azure Cognitive Services' OCR extracts text.  
   - Image processing is executed in parallel using asynchronous requests, ensuring efficiency.  

3. **Query Handling & Vector Search**  
   - User queries expanded by ChatGPT to search deep in database
   - Enhanced User queries are processed through a vector database (Weaviate).  
   - The system searches for the nearest text vectors and re-ranks results for accuracy. 

---


## Design Write-Up

### Design Choices and Trade-offs  

1. **Initial Approach: Simple PDF Text Extraction**  
   - Initially, we extracted text directly from PDFs and docx.  
   - However, scanned documents contained only images, requiring an OCR solution.  

2. **Adding Azure Cognitive Services for OCR**  
   - To handle PDFs and docs with images, Azure OCR was integrated.  
   - This improved text extraction but introduced additional API costs and latency.  

3. **Hybrid Search for Improved Query Handling**  
   - A combination of **vector search** (semantic search using embeddings) and **keyword-based search** improves the accuracy of retrieval.  
   - Vector search finds semantically similar text, while keyword search ensures direct matches are also considered.  

4. **Query Expansion for Better Search Results**  
   - Simple queries sometimes failed to retrieve relevant results.  
   - An **LLM-based query expansion mechanism** was added to enhance search coverage.  
   - This ensures user queries reach a broader set of relevant documents.   

---

