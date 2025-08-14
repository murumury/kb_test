# kb_test

This repository provides a local RAG demo comparing three Python stacks: LangChain, LlamaIndex, and Haystack. A unified configuration file (`config/config.yaml`) controls loaders, chunking, embeddings, vector store options, retrieval parameters, and LLM settings so that only implementation details differ between stacks.

## Structure

- `config/config.yaml` – shared parameters
- `src/` – FastAPI server with pipelines for each framework
- `web/` – React interface to build knowledge bases and chat with the three pipelines

## Running
The project now includes dependency manifests for both sides:

- Python backend dependencies are listed in `requirements.txt`.
- Frontend dependencies are defined in `web/package.json`.

### One-click startup
Launching both the API server and React client together (with automatic dependency installation):

```bash
./start.sh
```

### Manual startup
If you prefer to set up manually:

```bash
pip install -r requirements.txt
uvicorn src.app:app --reload
```

In another terminal:

```bash
cd web
npm install
npm start
```

The code relies on external dependencies that may not be installed by default; the demo serves as a scaffold.
