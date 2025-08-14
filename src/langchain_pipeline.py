"""LangChain-based RAG pipeline."""

from typing import List, Tuple

# Placeholders for actual LangChain imports
try:
    from langchain.document_loaders import DirectoryLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import HuggingFaceEmbeddings
    from langchain.vectorstores import FAISS
    from langchain.chat_models import ChatOpenAI
    from langchain.chains import RetrievalQA
except Exception:  # pragma: no cover - dependency not installed
    DirectoryLoader = RecursiveCharacterTextSplitter = HuggingFaceEmbeddings = None
    FAISS = ChatOpenAI = RetrievalQA = None

from .common import load_config

_STORE: "FAISS" | None = None


def build() -> List[str]:
    """Build FAISS vector store using LangChain based on shared config."""
    global _STORE
    logs: List[str] = []
    cfg = load_config()
    if DirectoryLoader is None:
        logs.append("LangChain dependencies not installed")
        _STORE = None
        return logs
    loader = DirectoryLoader(cfg["loaders"]["directory"], glob=cfg["loaders"]["pattern"])
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
    embeddings = HuggingFaceEmbeddings(model_name=cfg["embedding"]["model"])
    logs.append("Creating FAISS store")
    _STORE = FAISS.from_documents(chunks, embeddings)
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
    llm = ChatOpenAI(model_name=cfg["llm"]["model"], temperature=cfg["llm"]["temperature"])
    chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
    logs.append("Running query")
    answer = chain.run(question)
    logs.append("Query complete")
    return answer, logs


def query(question: str) -> str:
    """Compatibility wrapper returning only the answer."""
    return query_with_logs(question)[0]

