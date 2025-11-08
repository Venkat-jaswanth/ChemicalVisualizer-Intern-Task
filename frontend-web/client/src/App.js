// frontend-web/client/src/App.js

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import DataVisualization from './components/DataVisualization';
import './App.css';

// The URL of our Django backend API
const API_URL = 'http://127.0.0.1:8000/api/datasets/';

function App() {
  const [selectedFile, setSelectedFile] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // --- NEW: Auth State ---
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const [latestDataset, setLatestDataset] = useState(null);
  const [history, setHistory] = useState([]);
  
  // We remove the automatic fetch on load
  // useEffect(() => {
  //   fetchHistory();
  // }, []);

  // --- API Functions ---
  const getAuth = () => {
    if (!username || !password) {
      setError("Please enter username and password.");
      return null;
    }
    return { username, password };
  }

  const fetchHistory = async () => {
    const auth = getAuth();
    if (!auth) return;

    setIsLoading(true);
    setError(null);
    try {
      const response = await axios.get(API_URL, { auth }); // <-- Pass auth
      
      setHistory(response.data);
      if (response.data.length > 0) {
        setLatestDataset(response.data[0]);
      } else {
        setLatestDataset(null);
      }
    } catch (err) {
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        setError('Login failed. Check username/password.');
      } else {
        setError('Failed to fetch history. Is the backend server running?');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileChange = (event) => {
    setSelectedFile(event.target.files[0]);
    setError(null); // Clear previous errors
  };

  const handleUpload = async () => {
    const auth = getAuth();
    if (!auth || !selectedFile) {
      setError('Please select a file and enter credentials.');
      return;
    }

    setIsLoading(true);
    setError(null);
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('name', selectedFile.name);

    try {
      const response = await axios.post(API_URL, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        auth: auth // <-- Pass auth
      });
      
      setLatestDataset(response.data); 
      fetchHistory(); // Refresh history
      setSelectedFile(null); 
    } catch (err) {
      if (err.response && (err.response.status === 401 || err.response.status === 403)) {
        setError('Login failed. Check username/password.');
      } else {
        setError('Upload failed. Please check the file (must be CSV) or console.');
      }
    } finally {
      setIsLoading(false);
    }
  };

const handleDownloadPDF = async (datasetId, datasetName) => {
    const auth = getAuth();
    if (!auth) return;

    try {
      const response = await axios.get(
        `${API_URL}${datasetId}/download_pdf/`, // e.g., /api/datasets/8/download_pdf/
        {
          auth: auth,
          responseType: 'blob' // <-- IMPORTANT: Tell axios we're expecting a file
        }
      );

      // Create a URL for the blob
      const fileURL = window.URL.createObjectURL(new Blob([response.data]));
      
      // Create a temporary link element to trigger the download
      const fileLink = document.createElement('a');
      fileLink.href = fileURL;
      const fileName = `${datasetName}_summary.pdf`;
      fileLink.setAttribute('download', fileName);
      
      // Append, click, and remove the link
      document.body.appendChild(fileLink);
      fileLink.click();
      document.body.removeChild(fileLink);
      window.URL.revokeObjectURL(fileURL); // Clean up the URL object

    } catch (err) {
      setError('Failed to download PDF.');
    }
  };


  return (
    <div className="App">
      <header className="App-header">
        <h1>🧪 Chemical Equipment Parameter Visualizer</h1>
      </header>
      
      <main className="container">
        
        {/* --- Section 1: Auth + Uploader --- */}
        <div className="card">
          <h2>Controls</h2>
          
          {/* --- NEW: Auth Form --- */}
          <div className="auth-form">
            <div className="form-group">
              <label>Username</label>
              <input 
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)} 
              />
            </div>
            <div className="form-group">
              <label>Password</label>
              <input 
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)} 
              />
            </div>
          </div>
          
          <button onClick={fetchHistory} disabled={isLoading}>
            {isLoading ? 'Loading...' : 'Login & Fetch History'}
          </button>
          
          <hr className="divider" />
          
          <p>Upload a .csv file:</p>
          <input type="file" accept=".csv" onChange={handleFileChange} />
          <button onClick={handleUpload} disabled={isLoading || !selectedFile}>
            {isLoading ? 'Uploading...' : 'Upload & Analyze'}
          </button>
          
          {error && <p className="error-message">{error}</p>}
        </div>

        {/* --- Section 2: Main Visualization --- */}
        <div className="card">
          <h2>Latest Dataset Analysis</h2>
          <DataVisualization summary={latestDataset?.summary} />
        </div>

        {/* --- Section 3: History --- */}
        <div className="card">
        <h2>Upload History (Last 5)</h2>
        <div className="history-list">
          {/* ... (no uploads message) ... */}
          {history.map((dataset) => (
            <div
              key={dataset.id}
              className={`history-item ${latestDataset?.id === dataset.id ? 'active' : ''}`}
            >
              {/* --- MODIFIED: Wrap info in a div to separate from button --- */}
              <div 
                className="history-item-info"
                onClick={() => setLatestDataset(dataset)}
              >
                <strong>{dataset.name}</strong>
                <span>{new Date(dataset.uploaded_at).toLocaleString()}</span>
              </div>
              
              {/* --- NEW: Download Button --- */}
              <button 
                className="download-btn"
                onClick={() => handleDownloadPDF(dataset.id, dataset.name)}
              >
                Download PDF
              </button>
            </div>
          ))}
        </div>
      </div>
        
      </main>
    </div>
  );
}

export default App;