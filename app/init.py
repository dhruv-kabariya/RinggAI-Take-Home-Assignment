from contextlib import asynccontextmanager
from fastapi import FastAPI

from services.weaviate import WeaviateService

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to Weaviate
    WeaviateService().connect()
    # ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # disconnect at end of server
    WeaviateService().disconnect()
