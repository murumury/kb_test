# kb_test

This repository provides a skeleton for a local RAG demo comparing three Python stacks: LangChain, LlamaIndex, and Haystack. A unified configuration file (`config/config.yaml`) controls loaders, chunking, embeddings, vector store options, retrieval parameters, and LLM settings. Each stack reads from this config so that only implementation details differ.

## Structure

- `config/config.yaml` – shared parameters
- `src/` – minimal pipeline definitions for each framework
- `web/` – placeholder React interface to chat with the three pipelines and trigger knowledge-base builds

The code is illustrative and relies on external dependencies that are not installed in this environment. Real implementations would need additional error handling and API endpoints to connect the React interface with backend pipelines.

