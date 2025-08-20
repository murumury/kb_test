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
    <div>
      <h2>{label}</h2>
      <input value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={handleAsk}>Ask</button>
      <p>{answer}</p>
      <pre>{logs.join('\n')}</pre>
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
    const value = e.target.type === 'number'
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
    <div>
      <h1>RAG Demo</h1>
      {config && (
        <div>
          <h2>配置</h2>
          <div>
            <h3>加载器</h3>
            <label>目录: <input value={config.loaders.directory} onChange={handleConfigChange('loaders', 'directory')} /></label>
            <label>模式: <input value={config.loaders.pattern} onChange={handleConfigChange('loaders', 'pattern')} /></label>
          </div>
          <div>
            <h3>切片</h3>
            <label>大小: <input type="number" value={config.chunking.chunk_size} onChange={handleConfigChange('chunking', 'chunk_size')} /></label>
            <label>重叠: <input type="number" value={config.chunking.overlap} onChange={handleConfigChange('chunking', 'overlap')} /></label>
          </div>
          <div>
            <h3>Embedding</h3>
            <label>模型: <input value={config.embedding.model} onChange={handleConfigChange('embedding', 'model')} /></label>
          </div>
          <div>
            <h3>向量库</h3>
            <label>类型: <input value={config.vector_store.type} onChange={handleConfigChange('vector_store', 'type')} /></label>
            <label>维度: <input type="number" value={config.vector_store.dimension} onChange={handleConfigChange('vector_store', 'dimension')} /></label>
            <label>度量: <input value={config.vector_store.metric} onChange={handleConfigChange('vector_store', 'metric')} /></label>
          </div>
          <div>
            <h3>检索</h3>
            <label>Top K: <input type="number" value={config.retrieval.top_k} onChange={handleConfigChange('retrieval', 'top_k')} /></label>
            <label>Reranker: <input value={config.retrieval.reranker || ''} onChange={handleConfigChange('retrieval', 'reranker')} /></label>
            <label>Hybrid: <input type="checkbox" checked={config.retrieval.hybrid} onChange={handleConfigChange('retrieval', 'hybrid')} /></label>
          </div>
          <div>
            <h3>LLM</h3>
            <label>Provider: <input value={config.llm.provider} onChange={handleConfigChange('llm', 'provider')} /></label>
            <label>模型: <input value={config.llm.model} onChange={handleConfigChange('llm', 'model')} /></label>
            <label>Temperature: <input type="number" step="0.1" value={config.llm.temperature} onChange={handleConfigChange('llm', 'temperature')} /></label>
          </div>
          <button onClick={handleSaveConfig}>保存配置</button>
        </div>
      )}
      <button onClick={handleBuild}>Build Knowledge Bases</button>
      {Object.entries(buildLogs).map(([name, logs]) => (
        <div key={name}>
          <h3>{name} build</h3>
          <pre>{(logs || []).join('\n')}</pre>
        </div>
      ))}
      <ChatPanel label="LangChain" pipeline="langchain" />
      <ChatPanel label="LlamaIndex" pipeline="llamaindex" />
      <ChatPanel label="Haystack" pipeline="haystack" />
    </div>
  );
}

