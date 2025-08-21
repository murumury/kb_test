# kb_test

此仓库提供一个本地的 RAG 演示，对比 LangChain、LlamaIndex 和 Haystack 三个 Python 技术栈。前端界面使用 Tailwind CSS 与 DaisyUI，风格简约现代。通过统一的配置文件（`config/config.yaml`）管理加载器、切片、向量化、向量库选项、检索参数和 LLM 设置，各技术栈之间仅实现细节不同。默认读取 `docs` 目录下的 `txt`、`md`、`pdf` 文件。也可以在前端页面直接修改上述配置，无需手动编辑 YAML。

## 目录结构

- `docs/` – 存放知识库文档（支持 `txt`、`md`、`pdf`）
- `config/config.yaml` – 共享参数
- `src/` – 基于 FastAPI 的服务器，包含每个框架的流水线
  - `web/` – 基于 React + Tailwind CSS 的前端，用于构建知识库并与三种流水线聊天

## 运行方式

项目包含后端和前端的依赖清单：

- Python 后端依赖位于 `requirements.txt`
- 前端依赖位于 `web/package.json`

### 一键启动

自动安装依赖并同时启动 API 服务和 React 客户端：

```bash
./start.sh
```

### 手动启动

如需手动设置：

```bash
pip install -r requirements.txt
uvicorn src.app:app --reload
```

另开一个终端：

```bash
cd web
npm install
npm start
```

### 环境变量

将 `.env.example` 复制为 `.env` 并在其中填写 API Key 等敏感信息。

也可以在前端页面的配置表单中直接设置 Embedding、Reranker 和 LLM 模型的 API Key 与 Base URL。
当需要重新构建知识库时，可点击页面上的「清除历史数据」按钮删除生成的 FAISS 索引和 SQLite 数据库。

代码依赖于外部服务，本演示仅提供基础骨架。
