"""FastAPI server exposing build and query endpoints for RAG pipelines."""

from typing import Any, Dict, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from . import haystack_pipeline, langchain_pipeline, llamaindex_pipeline
from .common import load_config, save_config, clear_history

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


class ClearResponse(BaseModel):
    logs: List[str]


class ConfigModel(BaseModel):
    loaders: Dict[str, Any]
    chunking: Dict[str, Any]
    embedding: Dict[str, Any]
    vector_store: Dict[str, Any]
    retrieval: Dict[str, Any]
    llm: Dict[str, Any]


@app.get("/config", response_model=ConfigModel)
def get_config() -> ConfigModel:
    """Return current configuration."""
    return ConfigModel(**load_config())


@app.post("/config", response_model=ConfigModel)
def update_config(cfg: ConfigModel) -> ConfigModel:
    """Update configuration and persist to disk."""
    save_config(cfg.dict())
    return cfg


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


@app.post("/clear", response_model=ClearResponse)
def clear() -> ClearResponse:
    """删除 FAISS 索引和数据库文件。"""
    logs = clear_history()
    return ClearResponse(logs=logs)


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

