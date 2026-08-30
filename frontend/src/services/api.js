// Centralized API layer for talking to the FastAPI backend.
//
// Every backend call funnels through `request()` so error handling
// (network failures, 4xx/5xx responses, FastAPI validation errors) is
// consistent everywhere it's used.

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

/** Error shape thrown by every function in this module. */
export class ApiError extends Error {
  constructor(message, { status = null, body = null } = {}) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.body = body;
  }

  /** True when the request never reached the server. */
  get isNetworkError() {
    return this.status === null;
  }
}

function messageForStatus(status) {
  switch (status) {
    case 400:
      return "The request was invalid.";
    case 404:
      return "The requested resource was not found.";
    case 413:
      return "That file is too large to upload.";
    case 415:
      return "That file type isn't supported.";
    case 422:
      return "The submitted data could not be validated.";
    case 502:
      return "The document intelligence service is temporarily unavailable. Please try again shortly.";
    case 500:
      return "Something went wrong on the server.";
    default:
      return `Request failed (${status}).`;
  }
}

/** Extracts a human-readable message from a FastAPI error body. */
function extractErrorMessage(body, status) {
  if (body) {
    // FastAPI HTTPException -> {"detail": "..."}
    if (typeof body.detail === "string" && body.detail.trim()) {
      return body.detail;
    }

    // FastAPI 422 validation errors -> {"detail": [{loc, msg, type}, ...]}
    if (Array.isArray(body.detail) && body.detail.length > 0) {
      return body.detail
        .map((err) => {
          const field = Array.isArray(err.loc) ? err.loc.at(-1) : null;
          return field ? `${field}: ${err.msg}` : err.msg;
        })
        .join("; ");
    }

    // Custom pipeline error shape -> {"stage": "ocr", "detail": "..."}
    if (body.stage && body.detail) {
      return `${body.stage} stage failed: ${body.detail}`;
    }
  }

  return messageForStatus(status);
}

/**
 * Performs a fetch against the API, throwing a normalized ApiError
 * for both network failures and non-2xx responses.
 */
async function request(path, options = {}) {
  let response;

  try {
    response = await fetch(`${API_BASE_URL}${path}`, options);
  } catch (networkError) {
    throw new ApiError(
      "Could not reach the server. Check your connection and that the backend is running.",
      { body: networkError },
    );
  }

  const contentType = response.headers.get("content-type") || "";
  let body = null;

  if (contentType.includes("application/json")) {
    body = await response.json().catch(() => null);
  }

  if (!response.ok) {
    throw new ApiError(extractErrorMessage(body, response.status), {
      status: response.status,
      body,
    });
  }

  return body;
}

/**
 * Uploads a document for OCR + semantic indexing + extraction.
 * This is the endpoint that makes a document queryable via /qa.
 */
export async function uploadDocument(file, documentType = "auto") {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("document_type", documentType);

  return request("/documents/process", {
    method: "POST",
    body: formData,
  });
}

/** Lists previously processed documents. */
export async function listDocuments({ skip = 0, limit = 50 } = {}) {
  const params = new URLSearchParams({ skip, limit });
  return request(`/documents?${params.toString()}`);
}

/** Fetches a single document's metadata, OCR result, and extraction result. */
export async function getDocument(documentId) {
  return request(`/documents/${documentId}`);
}

/**
 * Asks a question against the indexed documents.
 * Pass `documentId` to restrict retrieval to a single document.
 */
export async function askQuestion({ query, documentId = null, limit = 5 }) {
  return request("/qa", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      query,
      document_id: documentId,
      limit,
    }),
  });
}
