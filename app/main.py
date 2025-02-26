from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import uvicorn

from init import lifespan
from services.document import process_document
from services.weaviate import WeaviateService
from services.llm_service import QueryEnhancer
from utils.hash_generator import generate_document_id
from models.api import QueryRequest, QueryResponse, ResponseModel, DocumentMetadata

ragApp = FastAPI(
    title="RinggAI Backend Task",
    version="1.0.0",
    lifespan = lifespan,
)

# Add CORS middleware
ragApp.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@ragApp.post("/documents/upload",response_model=ResponseModel[DocumentMetadata])
async def upload_document(
    file: UploadFile = File(...),
):
    """
    Upload a new document for processing and embedding generation.
    Supports PDF, DOCX, JSON, and TXT formats.
    """
    try:
        docId =generate_document_id(file.filename)
        # read file and create chunking
        chunks,metadata = await process_document(file=file,docId=docId)
        # save to waveate 
        await WeaviateService().store_document(doc_id=docId,chunks=chunks,metadata=metadata)
        
        return ResponseModel(
                status=200,
                message="File Uploaded Successfuly",
                data=metadata,  
            )
    except Exception as e:
        return ResponseModel(
                status=400,
                error=str(e),
                message="Error While Uploading File",
                
            )
        # raise HTTPException(status_code=400, detail=str(e))


@ragApp.post("/query", response_model=ResponseModel[QueryResponse])
async def query_document(query: QueryRequest):
    """
    Query against specific documents to retrieve relevant information.
    """
    try:
        enhancce_query = QueryEnhancer().enhance_query(query.text)
        result = await WeaviateService().query(query_text= query.text,document_id= query.document_id,enhance_query=enhancce_query)
        return ResponseModel(
            data=result,
            status=200,
            message="Query executed successfully",
        )
    except Exception as e:
        return ResponseModel(
                status=400,
                error=str(e),
                message="Error While Executing Query"
            )
        # raise   HTTPException(status_code=400, detail=str(e))

@ragApp.get("/health")
async def health_check():
    # await WeaviateService().delete_collection()
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run("main:ragApp", host="0.0.0.0", port=8000, reload=True) 