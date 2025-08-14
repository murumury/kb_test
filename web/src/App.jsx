import React, { useState } from 'react';

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

  const handleBuild = async () => {
    const resp = await fetch('/build', { method: 'POST' });
    const data = await resp.json();
    setBuildLogs(data.logs || {});
  };

  return (
    <div>
      <h1>RAG Demo</h1>
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

