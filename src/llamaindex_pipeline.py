"""LlamaIndex-based RAG pipeline."""

# Placeholder imports
try:
    from llama_index import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
    from llama_index.llms import OpenAI
    from llama_index.embeddings import HuggingFaceEmbedding
except Exception:  # pragma: no cover - dependency not installed
    SimpleDirectoryReader = VectorStoreIndex = ServiceContext = None
    OpenAI = HuggingFaceEmbedding = None

from .common import load_config


def build_index() -> "VectorStoreIndex":
    cfg = load_config()
    reader = SimpleDirectoryReader(cfg["loaders"]["directory"], recursive=True)
    docs = reader.load_data()
    embed_model = HuggingFaceEmbedding(model_name=cfg["embedding"]["model"])
    service_context = ServiceContext.from_defaults(embed_model=embed_model, chunk_size=cfg["chunking"]["chunk_size"])
    return VectorStoreIndex.from_documents(docs, service_context=service_context)


def query(question: str) -> str:
    cfg = load_config()
    index = build_index()
    query_engine = index.as_query_engine(similarity_top_k=cfg["retrieval"]["top_k"])
    response = query_engine.query(question)
    return str(response)

