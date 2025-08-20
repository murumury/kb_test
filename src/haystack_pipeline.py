"""Haystack-based RAG pipeline."""

from pathlib import Path
from typing import List, Tuple, Optional

import requests

try:
    from haystack import Document
    from haystack.document_stores import FAISSDocumentStore
    from haystack.nodes import FARMReader, EmbeddingRetriever
except Exception:  # pragma: no cover - dependency not installed
    Document = FAISSDocumentStore = FARMReader = EmbeddingRetriever = None


from .common import load_config

_STORE: Optional[FAISSDocumentStore] = None


def siliconflow_rerank(query: str, docs: List[Document], model: str, api_key: str, base_url: str) -> List[Document]:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    payload = {"model": model, "query": query, "documents": [d.content for d in docs]}
    res = requests.post(base_url.rstrip("/"), json=payload, headers=headers, timeout=60)
    res.raise_for_status()
    j = res.json()
    items = j.get("data") or j.get("results") or []
    order = sorted(range(len(items)), key=lambda k: -(items[k].get("relevance_score", 0)))
    return [docs[i] for i in order]



def build() -> List[str]:
    """Construct FAISS document store and embed documents."""
    global _STORE
    logs: List[str] = []
    cfg = load_config()
    if FAISSDocumentStore is None:
        logs.append("Haystack dependencies not installed")
        _STORE = None
        return logs
    store = FAISSDocumentStore(
        embedding_dim=cfg["vector_store"]["dimension"],
        similarity=cfg["vector_store"]["metric"],
    )
    retriever = EmbeddingRetriever(
        document_store=None,
        embedding_model=cfg["embedding"]["model"],
        model_format="openai",
        api_key=cfg["embedding"]["api_key"],
        api_base=cfg["embedding"]["base_url"].rstrip("/").rsplit("/v1", 1)[0] + "/v1",

    )
    logs.append("Loading documents")
    docs: List[Document] = []
    directory = cfg["loaders"]["directory"]
    pattern = cfg["loaders"]["pattern"]
    for path in Path(directory).glob(pattern):
        ext = path.suffix.lower()
        if ext not in {".txt", ".md", ".pdf"}:
            continue
        if ext == ".pdf":
            try:
                from pypdf import PdfReader

                text = ""
                with open(path, "rb") as f:
                    reader = PdfReader(f)
                    for page in reader.pages:
                        text += page.extract_text() or ""
            except Exception:
                continue
        else:
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
        docs.append(Document(content=text, meta={"name": path.name}))
    if docs:
        embeddings = retriever.embed_documents(docs)
        for doc, emb in zip(docs, embeddings):
            doc.embedding = emb

        store.write_documents(docs)
    logs.append(f"Wrote {len(docs)} documents")
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
        document_store=None,
        embedding_model=cfg["embedding"]["model"],
        model_format="openai",
        api_key=cfg["embedding"]["api_key"],
        api_base=cfg["embedding"]["base_url"].rstrip("/").rsplit("/v1", 1)[0] + "/v1",
        top_k=cfg["retrieval"]["top_k"],
    )
    q_emb = retriever.embed_queries([question])[0]
    docs = _STORE.query_by_embedding(q_emb, top_k=cfg["retrieval"]["top_k"])
    if cfg["retrieval"].get("reranker"):
        docs = siliconflow_rerank(
            query=question,
            docs=docs,

            model=cfg["retrieval"]["reranker"],
            api_key=cfg["retrieval"]["reranker_api_key"],
            base_url=cfg["retrieval"]["reranker_base_url"],
        )

    reader = FARMReader(model_name_or_path=cfg["llm"]["model"])
    logs.append("Running query")
    result = reader.predict(query=question, documents=docs)
    logs.append("Query complete")
    answer = result["answers"][0].answer if result.get("answers") else ""
    return answer, logs


def query(question: str) -> str:
    return query_with_logs(question)[0]

