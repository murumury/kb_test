"""Entry point for building and querying three RAG pipelines."""

from . import langchain_pipeline, llamaindex_pipeline, haystack_pipeline

PIPELINES = {
    "langchain": langchain_pipeline,
    "llamaindex": llamaindex_pipeline,
    "haystack": haystack_pipeline,
}


def query(pipeline: str, question: str) -> str:
    """Route query to the selected pipeline."""
    if pipeline not in PIPELINES:
        raise ValueError(f"Unknown pipeline {pipeline}")
    return PIPELINES[pipeline].query(question)

