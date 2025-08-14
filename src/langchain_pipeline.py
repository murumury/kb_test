"""LangChain-based RAG pipeline."""

from typing import List

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


def build_vector_store() -> "FAISS":
    """Build FAISS vector store using LangChain based on shared config."""
    cfg = load_config()
    loader = DirectoryLoader(cfg["loaders"]["directory"], glob=cfg["loaders"]["pattern"])
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=cfg["chunking"]["chunk_size"],
        chunk_overlap=cfg["chunking"]["overlap"],
    )
    chunks = splitter.split_documents(docs)
    embeddings = HuggingFaceEmbeddings(model_name=cfg["embedding"]["model"])
    return FAISS.from_documents(chunks, embeddings)


def query(question: str) -> str:
    """Query the LangChain vector store with a question."""
    cfg = load_config()
    store = build_vector_store()
    retriever = store.as_retriever(search_type="similarity", search_kwargs={"k": cfg["retrieval"]["top_k"]})
    llm = ChatOpenAI(model_name=cfg["llm"]["model"], temperature=cfg["llm"]["temperature"])
    chain = RetrievalQA.from_chain_type(llm, retriever=retriever)
    return chain.run(question)

