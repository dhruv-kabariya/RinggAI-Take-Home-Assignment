import weaviate
from weaviate.classes.init import Auth
import weaviate.classes as wvc
from models.api import QueryResponse, TextSnippet
from typing import List, Dict, Optional
import json

from config import (
    WEAVIATE_URL,
    OPENAI_API_KEY,
    WEAVIATE_CLASS_NAME,
    WEAVIATE_API_KEY
)
class WeaviateService:
    _instance = None
    # client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(WeaviateService, cls).__new__(cls)
            cls._instance.client = None
        return cls._instance

    def connect(self):
        if self.client is None:
            self.client = weaviate.connect_to_weaviate_cloud(
                cluster_url=WEAVIATE_URL,
                auth_credentials=Auth.api_key(WEAVIATE_API_KEY),
                headers={
                    "X-OpenAI-Api-Key": OPENAI_API_KEY
                }
            )
            self._check_collection()

    def disconnect(self):
        if self.client is not None:
            self.client.close()
            self.client = None

    def _check_collection(self):
        """Ensure the required schema exists in Weaviate."""
        try:
            self.docs = self.client.collections.get(name=WEAVIATE_CLASS_NAME)
            exists = self.docs.exists()
                       
            if not exists:
                # Create the class if it doesn't exist
                self.docs = self.client.collections.create(
                    name=WEAVIATE_CLASS_NAME,
                    properties=[ 
                        wvc.config.Property(name="docId", data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="pageNo", data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="chunkId", data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="chunkDataType", data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="chunkData", data_type=wvc.config.DataType.TEXT),
                        wvc.config.Property(name="fileType", data_type=wvc.config.DataType.TEXT),
                    ],
                    vectorizer_config=wvc.config.Configure.Vectorizer.text2vec_openai(),
                    generative_config=wvc.config.Configure.Generative.openai(
                        model='gpt-4o',
                        max_tokens=1024
                        ),
                    )
                
        except Exception as e:
            raise Exception(f"Failed to ensure Weaviate schema: {str(e)}")

    async def store_document(self,doc_id:str,chunks:List, metadata: Dict):
        """Store document chunks in Weaviate."""
        try:
            # print(chunks)
            self.delete_document(document_id=doc_id)
            # Store each chunk with its metadata
            self.docs.data.insert_many(chunks)
        except Exception as e:
            # print(e)
            raise Exception(f"Failed to store document in Weaviate: {str(e)}")

    async def delete_document(self, document_id: str):
        """Delete all chunks belonging to a document."""
        try:
            self.docs.data.delete_many(
                where=weaviate.classes.query.Filter.by_property('docId').equal(document_id)
            )
        except Exception as e:
            raise Exception(f"Failed to delete document from Weaviate: {str(e)}")

    async def query(self, query_text: str, document_id: Optional[str] = None, limit: int = 5):
        """Query for relevant text chunks."""
        try:
            
            answers = self.docs.generate.near_text(
                query=query_text,
                filters=weaviate.classes.query.Filter.by_property('docId').equal(document_id),
                return_metadata=weaviate.classes.query.MetadataQuery(distance=True),
                grouped_task=query_text
            )
      
            snippets = []

            for item in answers.objects:
       
                snippets.append(
                    TextSnippet(
                        content=item.properties.get('chunkData'),
                        document_id=item.properties.get("docId"),
                        chunk_index=item.properties.get("chunkId"),
                        metadata=item.metadata.__dict__,
                        relevance_score=item.metadata.distance
                    )   
                )
          
            return QueryResponse(
                result= str(answers.generated),
                snippets= snippets,
                total_results=len(snippets)
            )
            
        except Exception as e:
            raise Exception(f"Failed to query Weaviate: {str(e)}")

    async def aggregate_json(self, query: Dict):
        """
        Bonus functionality: Perform aggregations on JSON data.
        This is a placeholder for the bonus JSON aggregation feature.
        """
        # TODO: Implement JSON aggregation functionality
        pass 