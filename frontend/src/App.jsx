import "./App.css";

function App() {
  return (
    <div className="app">
      <header className="topbar">
        <div>
          <h1>Enterprise Document Intelligence</h1>
          <p>AI-powered document understanding and retrieval</p>
        </div>

        <div className="status">
          <span className="status-dot" />
          System Ready
        </div>
      </header>

      <main className="workspace">
        <aside className="sidebar">
          <button className="upload-button">+ Upload Document</button>

          <div className="sidebar-section">
            <h2>Documents</h2>
            <p className="empty-state">No documents uploaded yet.</p>
          </div>
        </aside>

        <section className="content">
          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Upload & Documents</h2>
                <p>Add a document to start asking questions.</p>
              </div>
            </div>

            <div className="dropzone">
              <div className="upload-icon">↑</div>
              <h3>Drop your document here</h3>
              <p>or click to browse your files</p>
              <span>PDF, DOCX, TXT</span>
            </div>
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Ask Your Documents</h2>
                <p>Get answers using semantic search and RAG.</p>
              </div>
            </div>

            <div className="question-box">
              <input
                type="text"
                placeholder="Ask a question about your documents..."
              />
              <button>Ask</button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;