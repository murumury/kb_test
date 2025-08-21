"""LangChain-based RAG pipeline."""

from typing import List, Tuple, Optional

import requests

# Placeholders for actual LangChain imports (LangChain 0.2+ layout)
try:
    from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_openai import ChatOpenAI, OpenAIEmbeddings
    from langchain_community.vectorstores import FAISS
except Exception:  # pragma: no cover - dependency not installed
    DirectoryLoader = UnstructuredFileLoader = None
    RecursiveCharacterTextSplitter = None
    ChatOpenAI = OpenAIEmbeddings = None
    FAISS = None

from .common import load_config

_STORE: Optional[FAISS] = None


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
    """Build FAISS vector store using LangChain based on shared config."""
    global _STORE
    logs: List[str] = []
    cfg = load_config()
    if DirectoryLoader is None:
        logs.append("LangChain dependencies not installed")
        _STORE = None
        return logs
    loader = DirectoryLoader(
        cfg["loaders"]["directory"],
        glob=cfg["loaders"]["pattern"],
        loader_cls=UnstructuredFileLoader,
        silent_errors=True,
    )
    logs.append("Loading documents")
    docs = loader.load()
    logs.append(f"Loaded {len(docs)} documents")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg["chunking"]["chunk_size"],
        chunk_overlap=cfg["chunking"]["overlap"],
    )
    logs.append("Splitting documents")
    chunks = splitter.split_documents(docs)
    logs.append(f"Created {len(chunks)} chunks")
    emb = OpenAIEmbeddings(
        model=cfg["embedding"]["model"],
        api_key=cfg["embedding"]["api_key"],
        base_url=cfg["embedding"]["base_url"].rstrip("/").rsplit("/v1", 1)[0] + "/v1",
    )
    logs.append("Creating FAISS store")
    _STORE = FAISS.from_documents(chunks, emb)
    logs.append("Build complete")
    return logs


def query_with_logs(question: str) -> Tuple[str, List[str]]:
    """Query the LangChain vector store with a question, returning answer and logs."""
    global _STORE
    logs: List[str] = []
    if _STORE is None:
        logs.extend(build())
    if _STORE is None:
        return "LangChain dependencies missing", logs
    cfg = load_config()
    retriever = _STORE.as_retriever(search_type="similarity", search_kwargs={"k": cfg["retrieval"]["top_k"]})
    logs.append("Retrieving documents")
    docs = retriever.get_relevant_documents(question)
    if cfg["retrieval"].get("reranker"):
        order = siliconflow_rerank(
            query=question,
            docs=[d.page_content for d in docs],
            model=cfg["retrieval"]["reranker"],
            api_key=cfg["retrieval"]["reranker_api_key"],
            base_url=cfg["retrieval"]["reranker_base_url"],
        )
        docs = [docs[i] for i in order]
    llm = ChatOpenAI(model=cfg["llm"]["model"], temperature=cfg["llm"]["temperature"])
    context = "\n\n".join(d.page_content for d in docs)
    prompt = f"Use the following context to answer the question.\n{context}\n\nQuestion: {question}"
    logs.append("Running query")
    answer = llm.predict(prompt)
    logs.append("Query complete")
    return answer, logs


def query(question: str) -> str:
    """Compatibility wrapper returning only the answer."""
    return query_with_logs(question)[0]
