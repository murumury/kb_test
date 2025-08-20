import React, { useState, useEffect } from 'react';

function ChatPanel({ label, pipeline }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [logs, setLogs] = useState([]);

  const handleAsk = async () => {
    const resp = await fetch('/query', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ pipeline, question })
    });
    const data = await resp.json();
    setAnswer(data.answer);
    setLogs(data.logs || []);
  };

  return (
    <div className="card bg-base-100 shadow">
      <div className="card-body space-y-2">
        <h2 className="card-title">{label}</h2>
        <div className="flex gap-2">
          <input
            className="input input-bordered flex-1"
            value={question}
            onChange={e => setQuestion(e.target.value)}
            placeholder="请输入问题"
          />
          <button className="btn btn-primary" onClick={handleAsk}>提问</button>
        </div>
        {answer && <p className="whitespace-pre-wrap">{answer}</p>}
        {logs.length > 0 && (
          <pre className="text-xs bg-base-200 p-2 rounded">{logs.join('\n')}</pre>
        )}
      </div>
    </div>
  );
}

export default function App() {
  const [buildLogs, setBuildLogs] = useState({});
  const [config, setConfig] = useState(null);

  useEffect(() => {
    fetch('/config').then(res => res.json()).then(setConfig);
  }, []);

  const handleConfigChange = (section, key) => e => {
    const value =
      e.target.type === 'number'
        ? Number(e.target.value)
        : e.target.type === 'checkbox'
        ? e.target.checked
        : e.target.value;
    setConfig(prev => ({
      ...prev,
      [section]: { ...prev[section], [key]: value }
    }));
  };

  const handleSaveConfig = async () => {
    await fetch('/config', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
  };

  const handleBuild = async () => {
    const resp = await fetch('/build', { method: 'POST' });
    const data = await resp.json();
    setBuildLogs(data.logs || {});
  };

  return (
    <div className="min-h-screen bg-base-200 text-base-content">
      <div className="container mx-auto p-4 space-y-6">
        <h1 className="text-3xl font-bold text-center">RAG Demo</h1>

        {config && (
          <div className="bg-base-100 shadow rounded p-4 space-y-4">
            <h2 className="text-2xl font-semibold">配置</h2>
            <div className="grid gap-4 md:grid-cols-2">
              <div className="space-y-2">
                <h3 className="font-medium">加载器</h3>
                <label className="form-control">
                  <span className="label-text">目录</span>
                  <input
                    className="input input-bordered"
                    value={config.loaders.directory}
                    onChange={handleConfigChange('loaders', 'directory')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">模式</span>
                  <input
                    className="input input-bordered"
                    value={config.loaders.pattern}
                    onChange={handleConfigChange('loaders', 'pattern')}
                  />
                </label>
              </div>

              <div className="space-y-2">
                <h3 className="font-medium">切片</h3>
                <label className="form-control">
                  <span className="label-text">大小</span>
                  <input
                    type="number"
                    className="input input-bordered"
                    value={config.chunking.chunk_size}
                    onChange={handleConfigChange('chunking', 'chunk_size')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">重叠</span>
                  <input
                    type="number"
                    className="input input-bordered"
                    value={config.chunking.overlap}
                    onChange={handleConfigChange('chunking', 'overlap')}
                  />
                </label>
              </div>

              <div className="space-y-2">
                <h3 className="font-medium">Embedding</h3>
                <label className="form-control">
                  <span className="label-text">模型</span>
                  <input
                    className="input input-bordered"
                    value={config.embedding.model}
                    onChange={handleConfigChange('embedding', 'model')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">API Key</span>
                  <input
                    className="input input-bordered"
                    value={config.embedding.api_key}
                    onChange={handleConfigChange('embedding', 'api_key')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">Base URL</span>
                  <input
                    className="input input-bordered"
                    value={config.embedding.base_url}
                    onChange={handleConfigChange('embedding', 'base_url')}
                  />
                </label>
              </div>

              <div className="space-y-2">
                <h3 className="font-medium">向量库</h3>
                <label className="form-control">
                  <span className="label-text">类型</span>
                  <input
                    className="input input-bordered"
                    value={config.vector_store.type}
                    onChange={handleConfigChange('vector_store', 'type')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">维度</span>
                  <input
                    type="number"
                    className="input input-bordered"
                    value={config.vector_store.dimension}
                    onChange={handleConfigChange('vector_store', 'dimension')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">度量</span>
                  <input
                    className="input input-bordered"
                    value={config.vector_store.metric}
                    onChange={handleConfigChange('vector_store', 'metric')}
                  />
                </label>
              </div>

              <div className="space-y-2">
                <h3 className="font-medium">检索</h3>
                <label className="form-control">
                  <span className="label-text">Top K</span>
                  <input
                    type="number"
                    className="input input-bordered"
                    value={config.retrieval.top_k}
                    onChange={handleConfigChange('retrieval', 'top_k')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">Reranker</span>
                  <input
                    className="input input-bordered"
                    value={config.retrieval.reranker || ''}
                    onChange={handleConfigChange('retrieval', 'reranker')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">Reranker API Key</span>
                  <input
                    className="input input-bordered"
                    value={config.retrieval.reranker_api_key}
                    onChange={handleConfigChange('retrieval', 'reranker_api_key')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">Reranker Base URL</span>
                  <input
                    className="input input-bordered"
                    value={config.retrieval.reranker_base_url}
                    onChange={handleConfigChange('retrieval', 'reranker_base_url')}
                  />
                </label>
                <label className="flex items-center gap-2 cursor-pointer">
                  <span className="label-text">Hybrid</span>
                  <input
                    type="checkbox"
                    className="toggle"
                    checked={config.retrieval.hybrid}
                    onChange={handleConfigChange('retrieval', 'hybrid')}
                  />
                </label>
              </div>

              <div className="space-y-2">
                <h3 className="font-medium">LLM</h3>
                <label className="form-control">
                  <span className="label-text">Provider</span>
                  <input
                    className="input input-bordered"
                    value={config.llm.provider}
                    onChange={handleConfigChange('llm', 'provider')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">模型</span>
                  <input
                    className="input input-bordered"
                    value={config.llm.model}
                    onChange={handleConfigChange('llm', 'model')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">Temperature</span>
                  <input
                    type="number"
                    step="0.1"
                    className="input input-bordered"
                    value={config.llm.temperature}
                    onChange={handleConfigChange('llm', 'temperature')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">API Key</span>
                  <input
                    className="input input-bordered"
                    value={config.llm.api_key}
                    onChange={handleConfigChange('llm', 'api_key')}
                  />
                </label>
                <label className="form-control">
                  <span className="label-text">Base URL</span>
                  <input
                    className="input input-bordered"
                    value={config.llm.base_url}
                    onChange={handleConfigChange('llm', 'base_url')}
                  />
                </label>
              </div>
            </div>
            <button className="btn btn-primary" onClick={handleSaveConfig}>保存配置</button>
          </div>
        )}

        <button className="btn btn-secondary" onClick={handleBuild}>
          构建知识库
        </button>

        {Object.entries(buildLogs).map(([name, logs]) => (
          <div key={name} className="bg-base-100 shadow rounded p-4">
            <h3 className="font-medium">{name} build</h3>
            <pre className="text-sm whitespace-pre-wrap">{(logs || []).join('\n')}</pre>
          </div>
        ))}

        <div className="grid gap-4 md:grid-cols-3">
          <ChatPanel label="LangChain" pipeline="langchain" />
          <ChatPanel label="LlamaIndex" pipeline="llamaindex" />
          <ChatPanel label="Haystack" pipeline="haystack" />
        </div>
      </div>
    </div>
  );
}
