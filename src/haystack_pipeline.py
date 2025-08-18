"""Haystack-based RAG pipeline."""

from pathlib import Path
from typing import List, Tuple, Optional

# Placeholder imports
try:
    from haystack import Document
    from haystack.nodes import EmbeddingRetriever, FARMReader
    from haystack.document_stores import FAISSDocumentStore
    from haystack.pipelines import ExtractiveQAPipeline
except Exception:  # pragma: no cover - dependency not installed
    Document = EmbeddingRetriever = FARMReader = FAISSDocumentStore = ExtractiveQAPipeline = None

from .common import load_config

_STORE: Optional[FAISSDocumentStore] = None


def build() -> List[str]:
    """Construct FAISS document store and embed documents."""
    global _STORE
    logs: List[str] = []
    cfg = load_config()
    if FAISSDocumentStore is None:
        logs.append("Haystack dependencies not installed")
        _STORE = None
        return logs
    store = FAISSDocumentStore(embedding_dim=cfg["vector_store"]["dimension"], similarity=cfg["vector_store"]["metric"])
    retriever = EmbeddingRetriever(
        document_store=store,
        embedding_model=cfg["embedding"]["model"],
        top_k=cfg["retrieval"]["top_k"],
    )
    logs.append("Loading documents")
    docs = []
    directory = cfg["loaders"]["directory"]
    pattern = cfg["loaders"]["pattern"]
    for path in Path(directory).glob(pattern):
        with open(path, "r", encoding="utf-8") as f:
            docs.append(Document(content=f.read(), meta={"name": path.name}))
    store.write_documents(docs)
    logs.append(f"Wrote {len(docs)} documents")
    logs.append("Updating embeddings")
    store.update_embeddings(retriever)
    logs.append("Build complete")
    _STORE = store
    return logs


def query_with_logs(question: str) -> Tuple[str, List[str]]:
    """Query the Haystack store and return answer and logs."""
    global _STORE
    logs: List[str] = []
    if _STORE is None:
        logs.extend(build())
    if _STORE is None:
        return "Haystack dependencies missing", logs
    cfg = load_config()
    retriever = EmbeddingRetriever(
        document_store=_STORE,
        embedding_model=cfg["embedding"]["model"],
        top_k=cfg["retrieval"]["top_k"],
    )
    reader = FARMReader(model_name_or_path=cfg["llm"]["model"])
    pipeline = ExtractiveQAPipeline(reader, retriever)
    logs.append("Running query")
    result = pipeline.run(query=question, params={"Retriever": {"top_k": cfg["retrieval"]["top_k"]}})
    logs.append("Query complete")
    answer = result["answers"][0].answer if result.get("answers") else ""
    return answer, logs


def query(question: str) -> str:
    return query_with_logs(question)[0]

