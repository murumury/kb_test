"""LlamaIndex-based RAG pipeline."""

from typing import List, Tuple, Optional

# Placeholder imports (LlamaIndex 0.10–0.12 layout)
try:
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.huggingface import HuggingFaceEmbedding
except Exception:  # pragma: no cover - dependency not installed
    SimpleDirectoryReader = None
    VectorStoreIndex = None
    ServiceContext = None
    OpenAI = None
    HuggingFaceEmbedding = None

from .common import load_config

_INDEX: Optional[VectorStoreIndex] = None


def build() -> List[str]:
    """Build LlamaIndex index from documents."""
    global _INDEX
    logs: List[str] = []
    cfg = load_config()
    if SimpleDirectoryReader is None:
        logs.append("LlamaIndex dependencies not installed")
        _INDEX = None
        return logs
    reader = SimpleDirectoryReader(
        cfg["loaders"]["directory"],
        recursive=True,
        required_exts=[".txt", ".md", ".pdf"],
    )
    logs.append("Loading documents")
    docs = reader.load_data()
    logs.append(f"Loaded {len(docs)} documents")
    embed_model = HuggingFaceEmbedding(model_name=cfg["embedding"]["model"])
    service_context = ServiceContext.from_defaults(embed_model=embed_model, chunk_size=cfg["chunking"]["chunk_size"])
    logs.append("Building index")
    _INDEX = VectorStoreIndex.from_documents(docs, service_context=service_context)
    logs.append("Build complete")
    return logs


def query_with_logs(question: str) -> Tuple[str, List[str]]:
    """Query the LlamaIndex store and return answer and logs."""
    global _INDEX
    logs: List[str] = []
    if _INDEX is None:
        logs.extend(build())
    if _INDEX is None:
        return "LlamaIndex dependencies missing", logs
    cfg = load_config()
    query_engine = _INDEX.as_query_engine(similarity_top_k=cfg["retrieval"]["top_k"])
    logs.append("Running query")
    response = query_engine.query(question)
    logs.append("Query complete")
    return str(response), logs


def query(question: str) -> str:
    return query_with_logs(question)[0]

