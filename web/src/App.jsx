import React, { useState } from 'react';

function ChatPanel({ label, pipeline }) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');

  const handleAsk = () => {
    // Placeholder: in real app, call backend API
    setAnswer(`Placeholder answer from ${pipeline}: ${question}`);
  };

  return (
    <div>
      <h2>{label}</h2>
      <input value={question} onChange={e => setQuestion(e.target.value)} />
      <button onClick={handleAsk}>Ask</button>
      <p>{answer}</p>
    </div>
  );
}

export default function App() {
  return (
    <div>
      <h1>RAG Demo</h1>
      <ChatPanel label="LangChain" pipeline="langchain" />
      <ChatPanel label="LlamaIndex" pipeline="llamaindex" />
      <ChatPanel label="Haystack" pipeline="haystack" />
      <button>Build Knowledge Bases</button>
    </div>
  );
}

