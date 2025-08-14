"""FastAPI server exposing build and query endpoints for RAG pipelines."""

from typing import Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import haystack_pipeline, langchain_pipeline, llamaindex_pipeline

PIPELINES = {
    "langchain": langchain_pipeline,
    "llamaindex": llamaindex_pipeline,
    "haystack": haystack_pipeline,
}

app = FastAPI()


class QueryRequest(BaseModel):
    pipeline: str
    question: str


class QueryResponse(BaseModel):
    answer: str
    logs: List[str]


class BuildResponse(BaseModel):
    logs: Dict[str, List[str]]


@app.post("/build", response_model=BuildResponse)
def build() -> BuildResponse:
    """Trigger building all knowledge bases."""
    logs: Dict[str, List[str]] = {}
    for name, module in PIPELINES.items():
        if hasattr(module, "build"):
            logs[name] = module.build()
        else:
            logs[name] = ["build not implemented"]
    return BuildResponse(logs=logs)


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest) -> QueryResponse:
    """Query a specific pipeline."""
    if req.pipeline not in PIPELINES:
        raise HTTPException(status_code=400, detail="Unknown pipeline")
    module = PIPELINES[req.pipeline]
    if hasattr(module, "query_with_logs"):
        answer, logs = module.query_with_logs(req.question)
    else:
        answer = module.query(req.question)
        logs = []
    return QueryResponse(answer=answer, logs=logs)

