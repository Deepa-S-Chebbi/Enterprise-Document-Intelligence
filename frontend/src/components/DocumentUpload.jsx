import { useRef, useState } from "react";
import { uploadDocument, ApiError } from "../services/api";

const DOCUMENT_TYPES = [
  { value: "auto", label: "Auto-detect" },
  { value: "invoice", label: "Invoice" },
  { value: "resume", label: "Resume" },
  { value: "contract", label: "Contract" },
  { value: "purchase_order", label: "Purchase Order" },
  { value: "receipt", label: "Receipt" },
  { value: "bank_statement", label: "Bank Statement" },
];

/**
 * Handles picking/dropping a PDF and sending it through the
 * document processing pipeline (OCR + indexing + extraction).
 */
export default function DocumentUpload({ onUploaded }) {
  const [status, setStatus] = useState("idle"); // idle | uploading | success | error
  const [errorMessage, setErrorMessage] = useState(null);
  const [fileName, setFileName] = useState(null);
  const [documentType, setDocumentType] = useState("auto");
  const [isDragging, setIsDragging] = useState(false);
  const inputRef = useRef(null);

  async function handleFile(file) {
    if (!file) return;

    setFileName(file.name);
    setStatus("uploading");
    setErrorMessage(null);

    try {
      const result = await uploadDocument(file, documentType);
      setStatus("success");
      onUploaded?.(result);
    } catch (error) {
      setStatus("error");
      setErrorMessage(
        error instanceof ApiError
          ? error.message
          : "Something went wrong while uploading. Please try again.",
      );
    }
  }

  function handleInputChange(event) {
    const file = event.target.files?.[0];
    handleFile(file);
    // Allow re-selecting the same file after a failure/retry.
    event.target.value = "";
  }

  function handleDrop(event) {
    event.preventDefault();
    setIsDragging(false);
    const file = event.dataTransfer.files?.[0];
    handleFile(file);
  }

  function handleDragOver(event) {
    event.preventDefault();
    setIsDragging(true);
  }

  function handleDragLeave() {
    setIsDragging(false);
  }

  const isUploading = status === "uploading";

  return (
    <div className="upload-widget">
      <label className="document-type-field">
        Document type
        <select
          value={documentType}
          onChange={(e) => setDocumentType(e.target.value)}
          disabled={isUploading}
        >
          {DOCUMENT_TYPES.map((type) => (
            <option key={type.value} value={type.value}>
              {type.label}
            </option>
          ))}
        </select>
      </label>

      <div
        className={`dropzone${isDragging ? " dropzone-active" : ""}${
          isUploading ? " dropzone-busy" : ""
        }`}
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onClick={() => !isUploading && inputRef.current?.click()}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if ((e.key === "Enter" || e.key === " ") && !isUploading) {
            inputRef.current?.click();
          }
        }}
      >
        <input
          ref={inputRef}
          type="file"
          accept="application/pdf"
          hidden
          onChange={handleInputChange}
          disabled={isUploading}
        />

        {status === "uploading" && (
          <>
            <div className="upload-icon spin">↻</div>
            <h3>Processing {fileName}…</h3>
            <p>Running OCR, indexing, and extraction. This can take a moment.</p>
          </>
        )}

        {status !== "uploading" && (
          <>
            <div className="upload-icon">↑</div>
            <h3>Drop your document here</h3>
            <p>or click to browse your files</p>
            <span>PDF only</span>
          </>
        )}
      </div>

      {status === "success" && (
        <p className="upload-feedback upload-feedback-success">
          {fileName} was processed successfully and is ready for questions.
        </p>
      )}

      {status === "error" && (
        <p className="upload-feedback upload-feedback-error" role="alert">
          {errorMessage}
        </p>
      )}
    </div>
  );
}
