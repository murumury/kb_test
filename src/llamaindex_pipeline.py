"""LlamaIndex-based RAG pipeline."""

from typing import List, Tuple, Optional

import requests

# Placeholder imports (LlamaIndex 0.10–0.12 layout)
try:
    from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, ServiceContext
    from llama_index.llms.openai import OpenAI
    from llama_index.embeddings.openai import OpenAIEmbedding
except Exception:  # pragma: no cover - dependency not installed
    SimpleDirectoryReader = None
    VectorStoreIndex = None
    ServiceContext = None
    OpenAI = None
    OpenAIEmbedding = None

from .common import load_config

_INDEX: Optional[VectorStoreIndex] = None


def siliconflow_rerank(query: str, docs: List[str], model: str, api_key: str, base_url: str) -> List[int]:
    """Call SiliconFlow rerank API and return ordering indices."""
    url = base_url.rstrip("/")
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "query": query, "documents": docs}
    res = requests.post(url, json=payload, headers=headers, timeout=60)
    res.raise_for_status()
    data = res.json()
    items = data.get("data") or data.get("results") or []
    order = sorted(range(len(items)), key=lambda k: -(items[k].get("relevance_score", 0)))
    return order


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
    if not docs:
        logs.append("No documents loaded; skipping index build")
        _INDEX = None
        return logs

    embed_model = OpenAIEmbedding(
        model=cfg["embedding"]["model"],
        api_key=cfg["embedding"]["api_key"],
        api_base=cfg["embedding"]["base_url"].rstrip("/").rsplit("/v1", 1)[0] + "/v1",
    )
    service_context = ServiceContext.from_defaults(
        embed_model=embed_model,
        chunk_size=cfg["chunking"]["chunk_size"],
    )
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
    retriever = _INDEX.as_retriever(similarity_top_k=cfg["retrieval"]["top_k"])
    logs.append("Retrieving documents")
    nodes = retriever.retrieve(question)
    if cfg["retrieval"].get("reranker"):
        order = siliconflow_rerank(
            query=question,
            docs=[n.node.text for n in nodes],
            model=cfg["retrieval"]["reranker"],
            api_key=cfg["retrieval"]["reranker_api_key"],
            base_url=cfg["retrieval"]["reranker_base_url"],
        )
        nodes = [nodes[i] for i in order]
    llm = OpenAI(model=cfg["llm"]["model"], temperature=cfg["llm"]["temperature"])
    context = "\n\n".join(n.node.text for n in nodes)
    prompt = f"Use the following context to answer the question.\n{context}\n\nQuestion: {question}"
    logs.append("Running query")
    response = llm.complete(prompt)
    logs.append("Query complete")
    answer = getattr(response, "text", str(response))
    return answer, logs


def query(question: str) -> str:
    return query_with_logs(question)[0]

