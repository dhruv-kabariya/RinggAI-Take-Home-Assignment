from pydantic import BaseModel, Field
from typing import Optional, List, Dict, TypeVar, Generic
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseModel(GenericModel, Generic[T]):
    status:int
    error:Optional[str] = None
    message:Optional[str] = None
    data:Optional[T] = None

class QueryRequest(BaseModel):
    text: str = Field(..., description="The query text to search for")
    document_id: Optional[str] = Field(None, description="Optional document ID to restrict the search to")

class TextSnippet(BaseModel):
    content: str = Field(..., description="The retrieved text content")
    document_id: str = Field(..., description="The ID of the source document")
    chunk_index: str = Field(..., description="The index of the chunk within the document")
    metadata: Dict = Field(default_factory=dict, description="Additional metadata about the snippet")
    relevance_score: Optional[float] = Field(..., description="The relevance score of this snippet to the query")

class QueryResponse(BaseModel):
    snippets: List[TextSnippet] = Field(..., description="List of relevant text snippets")
    total_results: int = Field(..., description="Total number of results found")
    result:str = Field(...,description="Reply for Query")

class DocumentMetadata(BaseModel):
    document_id: str = Field(..., description="Unique ID for the document")
    file_name: str = Field(..., description="Original file name")
    file_type: str = Field(..., description="File type/extension")
    upload_timestamp: str = Field(..., description="Timestamp of upload")
    total_chunks: int = Field(..., description="Number of chunks the document was split into")
    additional_info: Dict = Field(default_factory=dict, description="Additional document metadata") 