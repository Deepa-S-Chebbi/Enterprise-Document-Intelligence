import { useState } from "react";
import { askQuestion, ApiError } from "../services/api";

/**
 * Sends a question to POST /api/v1/qa, optionally scoped to a
 * single document, and displays the returned RAG answer.
 */
export default function QuestionBox({ selectedDocumentId, selectedDocumentName }) {
  const [query, setQuery] = useState("");
  const [status, setStatus] = useState("idle"); // idle | asking | success | error
  const [answer, setAnswer] = useState(null);
  const [errorMessage, setErrorMessage] = useState(null);

  async function handleAsk(event) {
    event.preventDefault();

    const trimmed = query.trim();
    if (!trimmed || status === "asking") return;

    setStatus("asking");
    setErrorMessage(null);

    try {
      const result = await askQuestion({
        query: trimmed,
        documentId: selectedDocumentId,
      });
      setAnswer(result.answer);
      setStatus("success");
    } catch (error) {
      setStatus("error");
      setErrorMessage(
        error instanceof ApiError
          ? error.message
          : "Something went wrong while asking your question. Please try again.",
      );
    }
  }

  return (
    <div className="question-widget">
      <p className="question-scope">
        {selectedDocumentId
          ? `Asking within: ${selectedDocumentName ?? "selected document"}`
          : "Asking across all indexed documents"}
      </p>

      <form className="question-box" onSubmit={handleAsk}>
        <input
          type="text"
          placeholder="Ask a question about your documents..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={status === "asking"}
        />
        <button type="submit" disabled={status === "asking" || !query.trim()}>
          {status === "asking" ? "Asking…" : "Ask"}
        </button>
      </form>

      {status === "asking" && <p className="answer-loading">Thinking through your documents…</p>}

      {status === "error" && (
        <p className="answer-error" role="alert">
          {errorMessage}
        </p>
      )}

      {status === "success" && answer && (
        <div className="answer-card">
          <h3>Answer</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}
