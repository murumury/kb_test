# kb_test

This repository provides a local RAG demo comparing three Python stacks: LangChain, LlamaIndex, and Haystack. A unified configuration file (`config/config.yaml`) controls loaders, chunking, embeddings, vector store options, retrieval parameters, and LLM settings so that only implementation details differ between stacks.

## Structure

- `config/config.yaml` – shared parameters
- `src/` – FastAPI server with pipelines for each framework
- `web/` – React interface to build knowledge bases and chat with the three pipelines

## Running
Launch both the API server and React client together:

```bash
./start.sh
```

Alternatively, start the components manually.
First run the API server:

```bash
uvicorn src.app:app --reload
```

Then in another terminal start the React client:

```bash
cd web
npm start
```

The code relies on external dependencies that are not installed in this environment; the demo serves as a scaffold.

