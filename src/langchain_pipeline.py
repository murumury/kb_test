"""LangChain-based RAG pipeline."""

from typing import List, Tuple, Optional

# Placeholders for actual LangChain imports (LangChain 0.2+ layout)
try:
    from langchain_community.document_loaders import DirectoryLoader, UnstructuredFileLoader
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_openai import ChatOpenAI
    from langchain.chains import RetrievalQA
except Exception:  # pragma: no cover - dependency not installed
    DirectoryLoader = UnstructuredFileLoader = None
    RecursiveCharacterTextSplitter = None
    HuggingFaceEmbeddings = None
    FAISS = None
    ChatOpenAI = None
    RetrievalQA = None

from .common import load_config

_STORE: Optional[FAISS] = None


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
