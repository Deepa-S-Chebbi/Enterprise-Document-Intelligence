import { useCallback, useEffect, useMemo, useState } from "react";
import "./App.css";
import DocumentUpload from "./components/DocumentUpload";
import DocumentList from "./components/DocumentList";
import QuestionBox from "./components/QuestionBox";
import { listDocuments, ApiError } from "./services/api";

function App() {
  const [documents, setDocuments] = useState([]);
  const [documentsStatus, setDocumentsStatus] = useState("loading"); // loading | ready | error
  const [documentsError, setDocumentsError] = useState(null);
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);

  const refreshDocuments = useCallback(async () => {
    setDocumentsStatus("loading");
    setDocumentsError(null);

    try {
      const result = await listDocuments();
      setDocuments(result ?? []);
      setDocumentsStatus("ready");
    } catch (error) {
      setDocumentsStatus("error");
      setDocumentsError(
        error instanceof ApiError
          ? error.message
          : "Could not load documents. Please try again.",
      );
    }
  }, []);

  useEffect(() => {
    // Fire the initial load without awaiting it directly in the effect
    // body, so state updates happen asynchronously rather than
    // synchronously cascading off the effect itself.
    Promise.resolve().then(() => refreshDocuments());
  }, [refreshDocuments]);

  function handleUploaded(result) {
    // The processing pipeline returns the new document's id; refresh
    // the sidebar so the newly indexed document shows up right away.
    refreshDocuments();
    if (result?.document_id) {
      setSelectedDocumentId(result.document_id);
    }
  }

  const selectedDocumentName = useMemo(
    () =>
      documents.find((doc) => doc.id === selectedDocumentId)
        ?.original_filename ?? null,
    [documents, selectedDocumentId],
  );

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
          <div className="sidebar-section">
            <h2>Documents</h2>
            <DocumentList
              documents={documents}
              status={documentsStatus}
              errorMessage={documentsError}
              selectedDocumentId={selectedDocumentId}
              onSelect={setSelectedDocumentId}
              onRetry={refreshDocuments}
            />
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

            <DocumentUpload onUploaded={handleUploaded} />
          </div>

          <div className="panel">
            <div className="panel-header">
              <div>
                <h2>Ask Your Documents</h2>
                <p>Get answers using semantic search and RAG.</p>
              </div>
            </div>

            <QuestionBox
              selectedDocumentId={selectedDocumentId}
              selectedDocumentName={selectedDocumentName}
            />
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
