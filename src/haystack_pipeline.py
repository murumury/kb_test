"""Haystack-based RAG pipeline."""

# Placeholder imports
try:
    from haystack import Document
    from haystack.nodes import EmbeddingRetriever, FARMReader
    from haystack.document_stores import FAISSDocumentStore
    from haystack.pipelines import ExtractiveQAPipeline
except Exception:  # pragma: no cover - dependency not installed
    Document = EmbeddingRetriever = FARMReader = FAISSDocumentStore = ExtractiveQAPipeline = None

from .common import load_config


def build_document_store() -> "FAISSDocumentStore":
    cfg = load_config()
    store = FAISSDocumentStore(embedding_dim=cfg["vector_store"]["dimension"], similarity=cfg["vector_store"]["metric"])
    retriever = EmbeddingRetriever(
        document_store=store,
        embedding_model=cfg["embedding"]["model"],
        top_k=cfg["retrieval"]["top_k"],
    )
    # Loading documents is left as an exercise; placeholder
    return store


def query(question: str) -> str:
    cfg = load_config()
    store = build_document_store()
    reader = FARMReader(model_name_or_path=cfg["llm"]["model"])
    pipeline = ExtractiveQAPipeline(reader, None)
    result = pipeline.run(query=question, params={"Retriever": {"top_k": cfg["retrieval"]["top_k"]}})
    return str(result)

