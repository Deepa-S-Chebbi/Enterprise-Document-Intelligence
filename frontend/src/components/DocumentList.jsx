const STATUS_LABELS = {
  uploaded: "Uploaded",
  ocr_complete: "OCR complete",
  extraction_complete: "Ready",
  failed: "Failed",
};

function formatStatus(status) {
  return STATUS_LABELS[status] ?? status;
}

/**
 * Displays the documents returned by GET /api/v1/documents and lets
 * the user pick one to scope questions to.
 */
export default function DocumentList({
  documents,
  status, // "idle" | "loading" | "error" | "ready"
  errorMessage,
  selectedDocumentId,
  onSelect,
  onRetry,
}) {
  if (status === "loading") {
    return <p className="empty-state">Loading documents…</p>;
  }

  if (status === "error") {
    return (
      <div className="sidebar-error" role="alert">
        <p>{errorMessage}</p>
        <button type="button" className="link-button" onClick={onRetry}>
          Try again
        </button>
      </div>
    );
  }

  if (!documents || documents.length === 0) {
    return <p className="empty-state">No documents uploaded yet.</p>;
  }

  return (
    <ul className="document-list">
      <li>
        <button
          type="button"
          className={`document-item${
            selectedDocumentId === null ? " document-item-selected" : ""
          }`}
          onClick={() => onSelect(null)}
        >
          <span className="document-item-name">All documents</span>
          <span className="document-item-meta">Search everything indexed</span>
        </button>
      </li>

      {documents.map((doc) => (
        <li key={doc.id}>
          <button
            type="button"
            className={`document-item${
              selectedDocumentId === doc.id ? " document-item-selected" : ""
            }`}
            onClick={() => onSelect(doc.id)}
          >
            <span className="document-item-name">{doc.original_filename}</span>
            <span
              className={`document-item-meta status-${doc.status ?? "unknown"}`}
            >
              {formatStatus(doc.status)}
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
}
