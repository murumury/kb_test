"""Common utilities for loading configuration."""

from pathlib import Path
from typing import Any, Dict
import os

import yaml


def load_config(path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load YAML configuration file and populate relevant env vars."""
    with open(Path(path), "r", encoding="utf-8") as f:
        cfg: Dict[str, Any] = yaml.safe_load(f)

    emb = cfg.get("embedding", {})
    if emb.get("api_key"):
        os.environ["EMBEDDING_API_KEY"] = emb["api_key"]
    if emb.get("base_url"):
        os.environ["EMBEDDING_BASE_URL"] = emb["base_url"]

    ret = cfg.get("retrieval", {})
    if ret.get("reranker_api_key"):
        os.environ["RERANKER_API_KEY"] = ret["reranker_api_key"]
    if ret.get("reranker_base_url"):
        os.environ["RERANKER_BASE_URL"] = ret["reranker_base_url"]

    llm = cfg.get("llm", {})
    if llm.get("api_key"):
        os.environ["OPENAI_API_KEY"] = llm["api_key"]
    if llm.get("base_url"):
        os.environ["OPENAI_API_BASE"] = llm["base_url"]

    return cfg


def save_config(config: Dict[str, Any], path: str = "config/config.yaml") -> None:
    """Persist configuration to YAML file."""
    with open(Path(path), "w", encoding="utf-8") as f:
        yaml.safe_dump(config, f, allow_unicode=True)


def clear_history(path: Path = Path(".")) -> list[str]:
    """删除默认的 FAISS 索引和 SQLite 数据库文件。"""
    targets = [
        "faiss_document_store.db",
        "faiss_document_store.db-shm",
        "faiss_document_store.db-wal",
        "faiss_index.faiss",
        "faiss_index.json",
    ]
    logs: list[str] = []
    for name in targets:
        p = path / name
        if p.exists():
            p.unlink()
            logs.append(f"删除 {name}")
    if not logs:
        logs.append("未找到历史数据")
    return logs

