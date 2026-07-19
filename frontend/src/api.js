const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

export function getToken() {
  return localStorage.getItem("medical_ai_token") || "";
}

export function setToken(token) {
  if (token) {
    localStorage.setItem("medical_ai_token", token);
  } else {
    localStorage.removeItem("medical_ai_token");
  }
}

async function request(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  if (options.body && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  const contentType = response.headers.get("content-type") || "";
  const payload = contentType.includes("application/json")
    ? await response.json()
    : await response.text();

  if (!response.ok) {
    const message = payload?.detail || payload?.message || "Request failed";
    throw new Error(message);
  }

  return payload;
}

async function requestBlob(path) {
  const headers = new Headers();
  const token = getToken();

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers,
  });

  if (!response.ok) {
    throw new Error("File request failed");
  }

  return response.blob();
}

export const api = {
  baseUrl: API_BASE_URL,

  register: (email, password) =>
    request("/auth/register", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  login: (email, password) =>
    request("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    }),

  me: () => request("/auth/me"),

  listRecords: () => request("/records/"),

  createRecord: (record) =>
    request("/records/", {
      method: "POST",
      body: JSON.stringify(record),
    }),

  updateRecord: (id, record) =>
    request(`/records/${id}`, {
      method: "PUT",
      body: JSON.stringify(record),
    }),

  deleteRecord: (id) =>
    request(`/records/${id}`, {
      method: "DELETE",
    }),

  listDocuments: (medicalRecordId) => {
    const query = medicalRecordId ? `?medical_record_id=${medicalRecordId}` : "";
    return request(`/documents/${query}`);
  },

  uploadDocument: (medicalRecordId, file) => {
    const body = new FormData();
    body.append("medical_record_id", medicalRecordId);
    body.append("file", file);

    return request("/documents/upload", {
      method: "POST",
      body,
    });
  },

  deleteDocument: (id) =>
    request(`/documents/${id}`, {
      method: "DELETE",
    }),

  getOcrText: (id) => request(`/documents/${id}/ocr`),

  embedDocument: (id) =>
    request(`/documents/${id}/embed`, {
      method: "POST",
    }),

  searchDocuments: (medicalRecordId, query) =>
    request("/documents/search", {
      method: "POST",
      body: JSON.stringify({
        medical_record_id: medicalRecordId,
        query,
      }),
    }),

  listSessions: () => request("/sessions/"),

  createSession: (medicalRecordId, title) =>
    request("/sessions/", {
      method: "POST",
      body: JSON.stringify({
        medical_record_id: medicalRecordId,
        title,
      }),
    }),

  getSession: (id) => request(`/sessions/${id}`),

  // Requires the small backend patch included alongside this redesign
  // (GET /sessions/{id}/messages). Falls back gracefully if a 404/old
  // backend is deployed — see App.jsx's resumeSession().
  getSessionMessages: (id) => request(`/sessions/${id}/messages`),

  deleteSession: (id) =>
    request(`/sessions/${id}`, {
      method: "DELETE",
    }),

  chat: (sessionId, medicalRecordId, question) =>
    request("/chat/", {
      method: "POST",
      body: JSON.stringify({
        session_id: sessionId,
        medical_record_id: medicalRecordId,
        question,
      }),
    }),

  documentFileUrl: (id) => `${API_BASE_URL}/documents/${id}/file`,

  documentDownloadUrl: (id) => `${API_BASE_URL}/documents/${id}/download`,

  getDocumentFileBlob: (id) => requestBlob(`/documents/${id}/file`),

  getDocumentDownloadBlob: (id) => requestBlob(`/documents/${id}/download`),
};
