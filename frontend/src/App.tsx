import React, { useState } from 'react';
import axios from 'axios';

const App: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [uploadStatus, setUploadStatus] = useState('');

  const handleFileUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await axios.post('http://localhost:8000/api/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setUploadStatus(`Upload successful! File ID: ${res.data.file_id}`);
    } catch (err) {
      setUploadStatus('Upload failed');
      console.error(err);
    }
  };

  const handleQuerySubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await axios.post('http://localhost:8000/api/query', { query });
      setResponse(res.data.answer);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container">
      <h1>RAG Application</h1>
      
      <section>
        <h2>Upload Documents</h2>
        <form onSubmit={handleFileUpload}>
          <input 
            type="file" 
            onChange={(e) => setFile(e.target.files?.[0] || null)}
            accept=".pdf,.txt"
          />
          <button type="submit">Upload</button>
        </form>
        {uploadStatus && <p>{uploadStatus}</p>}
      </section>

      <section>
        <h2>Ask a Question</h2>
        <form onSubmit={handleQuerySubmit}>
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter your question..."
          />
          <button type="submit">Ask</button>
        </form>
        {response && (
          <div className="response">
            <h3>Answer:</h3>
            <p>{response}</p>
          </div>
        )}
      </section>
    </div>
  );
};

export default App;