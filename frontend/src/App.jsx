import React, { useEffect, useMemo, useState } from "react";
import { api, getToken, setToken } from "./api";
import { useToasts } from "./hooks/useToasts";
import AuthPanel from "./components/AuthPanel";
import PatientsPanel from "./components/PatientsPanel";
import ConversationPanel from "./components/ConversationPanel";
import ContextPanel from "./components/ContextPanel";
import DocumentViewerModal from "./components/DocumentViewerModal";
import Toasts from "./components/Toasts";
import VitalsTrace from "./components/VitalsTrace";
import { IconPanelLeft, IconPanelRight } from "./components/Icons";

export default function App() {
  const [authLoading, setAuthLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const [user, setUser] = useState(null);

  const [records, setRecords] = useState([]);
  const [recordsLoading, setRecordsLoading] = useState(false);
  const [selectedRecordId, setSelectedRecordId] = useState("");

  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [viewerDocument, setViewerDocument] = useState(null);

  const [sessions, setSessions] = useState([]);
  const [selectedSessionId, setSelectedSessionId] = useState("");
  const [messages, setMessages] = useState([]);
  const [messagesLoading, setMessagesLoading] = useState(false);
  const [historyUnavailable, setHistoryUnavailable] = useState(false);

  const [chatInput, setChatInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const [lastSources, setLastSources] = useState([]);
  const [lastSuggestedQuestions, setLastSuggestedQuestions] = useState([]);
  const [reportSummary, setReportSummary] = useState("");

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  const [requestsInFlight, setRequestsInFlight] = useState(0);
  const [mobilePanel, setMobilePanel] = useState("conversation");

  const { toasts, dismiss, runAction } = useToasts();

  const selectedRecord = useMemo(
    () => records.find((record) => String(record.id) === String(selectedRecordId)),
    [records, selectedRecordId]
  );

  const patientSessions = useMemo(
    () => sessions.filter((s) => String(s.medical_record_id) === String(selectedRecordId)),
    [sessions, selectedRecordId]
  );

  const selectedSession = useMemo(
    () => sessions.find((s) => String(s.id) === String(selectedSessionId)),
    [sessions, selectedSessionId]
  );

  function withTracking(label, action, opts) {
    setRequestsInFlight((n) => n + 1);
    return runAction(label, action, opts).finally(() => setRequestsInFlight((n) => Math.max(0, n - 1)));
  }

  // ---- authentication bootstrap ----
  useEffect(() => {
      async function bootstrap() {

          const token = getToken();

          if (!token) {
              setAuthenticated(false);
              setAuthLoading(false);
              return;
          }

          try {

              const me = await api.me();

              setUser(me);

              setAuthenticated(true);

          } catch {

              setToken("");

              setAuthenticated(false);

          } finally {

              setAuthLoading(false);

          }
      }

      bootstrap();

  }, []);

  // ---- workspace load ----
  useEffect(() => {

      if (!authenticated) return;

      (async () => {

          setRecordsLoading(true);

          try {

              const [patientRecords, chatSessions] =
                  await Promise.all([
                      api.listRecords(),
                      api.listSessions(),
                  ]);

              setRecords(patientRecords);

              setSessions(chatSessions);

              if (patientRecords.length > 0) {

                  selectRecord(
                      patientRecords[0].id,
                      chatSessions
                  );

              }

          } catch (error) {

              runAction(
                  "Load workspace",
                  () => Promise.reject(error)
              );

          } finally {

              setRecordsLoading(false);

          }

      })();

  }, [authenticated]);

  // ---- documents for selected patient ----
  useEffect(() => {
    if (!authenticated || !selectedRecordId) {
      setDocuments([]);
      return;
    }
    setDocumentsLoading(true);
    api
      .listDocuments(selectedRecordId)
      .then(setDocuments)
      .catch(() => setDocuments([]))
      .finally(() => setDocumentsLoading(false));
  }, [authenticated, selectedRecordId]);

  // ---- hydrate messages when the session changes ----
  useEffect(() => {
    if (!selectedSessionId) {
      setMessages([]);
      setHistoryUnavailable(false);
      return;
    }
    setMessagesLoading(true);
    setHistoryUnavailable(false);
    api
      .getSessionMessages(selectedSessionId)
      .then((history) => {
        setMessages(history.map((m) => ({ role: m.role, content: m.content, isNew: false })));
      })
      .catch(() => {
        setMessages([]);
        setHistoryUnavailable(true);
      })
      .finally(() => setMessagesLoading(false));
  }, [selectedSessionId]);

  function selectRecord(id, sessionList = sessions) {
    setSelectedRecordId(id);
    setLastSources([]);
    setLastSuggestedQuestions([]);
    setReportSummary("");
    setMobilePanel("conversation");

    const candidates = sessionList
      .filter((s) => String(s.medical_record_id) === String(id))
      .sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    setSelectedSessionId(candidates[0]?.id ? String(candidates[0].id) : "");
  }

  async function createPatient(payload) {
    const record = await withTracking("Create patient", () => api.createRecord(payload));
    setRecords((current) => [record, ...current]);
    selectRecord(record.id);
  }

  async function updatePatient(id, payload) {
    const updated = await withTracking("Update patient", () => api.updateRecord(id, payload));
    setRecords((current) => current.map((r) => (r.id === id ? updated : r)));
  }

  async function deletePatient(id) {
    await withTracking("Delete patient", () => api.deleteRecord(id));
    setRecords((current) => current.filter((r) => r.id !== id));
    if (String(selectedRecordId) === String(id)) {
      setSelectedRecordId("");
      setSelectedSessionId("");
      setDocuments([]);
      setMessages([]);
    }
  }

  async function uploadFiles(files) {
    for (const file of files) {
      // eslint-disable-next-line no-await-in-loop
      await withTracking(`Upload ${file.name}`, () => api.uploadDocument(selectedRecordId, file));
    }
    const docs = await api.listDocuments(selectedRecordId);
    setDocuments(docs);
  }

  async function deleteDocument(id) {
    await withTracking("Remove document", () => api.deleteDocument(id));
    setDocuments((current) => current.filter((d) => d.id !== id));
  }

  async function newConversation() {
    if (!selectedRecordId) return;
    const title = selectedRecord ? `${selectedRecord.patient_name} chat` : "Patient chat";
    const session = await withTracking("Start conversation", () =>
      api.createSession(Number(selectedRecordId), title)
    );
    setSessions((current) => [session, ...current]);
    setSelectedSessionId(String(session.id));
    setMessages([]);
    setLastSources([]);
    setLastSuggestedQuestions([]);
    setReportSummary("");
  }

  async function deleteSession(id) {
    await withTracking("Delete conversation", () => api.deleteSession(id));
    setSessions((current) => current.filter((s) => s.id !== id));
    if (String(selectedSessionId) === String(id)) {
      setSelectedSessionId("");
      setMessages([]);
    }
  }

  async function sendMessage(text) {
    const question = text.trim();
    if (!question || !selectedRecordId || isSending) return;

    let sessionId = selectedSessionId;
    if (!sessionId) {
      const title = selectedRecord ? `${selectedRecord.patient_name} chat` : "Patient chat";
      const session = await withTracking("Start conversation", () =>
        api.createSession(Number(selectedRecordId), title)
      );
      setSessions((current) => [session, ...current]);
      sessionId = String(session.id);
      setSelectedSessionId(sessionId);
    }

    setChatInput("");
    setMessages((current) => [...current, { role: "user", content: question, isNew: false }]);
    setIsSending(true);
    try {
      const response = await withTracking("Ask assistant", () =>
        api.chat(Number(sessionId), Number(selectedRecordId), question)
      );
      setMessages((current) => [
        ...current,
        { role: "assistant", content: response.answer, payload: response, isNew: true },
      ]);
      setLastSources(response.sources || []);
      setLastSuggestedQuestions(response.suggested_questions || []);
      if (response.intent === "REPORT_SUMMARY") setReportSummary(response.answer);
    } catch {
      // toast already shown
    } finally {
      setIsSending(false);
    }
  }

  async function searchDocuments(event) {
    event.preventDefault();
    if (!selectedRecordId || !searchQuery.trim()) return;
    setSearching(true);
    try {
      const result = await withTracking("Search documents", () =>
        api.searchDocuments(Number(selectedRecordId), searchQuery.trim())
      );
      setSearchResults(result);
    } finally {
      setSearching(false);
    }
  }

  function logout() {
    setToken("");
    setAuthLoading(false);
    setAuthenticated(false);
    setUser(null);
    setRecords([]);
    setDocuments([]);
    setSessions([]);
    setMessages([]);
    setSelectedRecordId("");
    setSelectedSessionId("");
    setSearchResults([]);
    setLastSources([]);
    setLastSuggestedQuestions([]);
    setReportSummary("");
  }

  if (authLoading) {
    return (
      <div className="loading-screen">
        <h1>NIGHTINGALE</h1>

        <p>Loading Clinical Workspace...</p>
      </div>
    );
  }

  if (!authenticated) {
    return (
      <>
        <AuthPanel
          runAction={runAction}
          onLogin={async () => {
            const me = await api.me();

            setUser(me);

            setAuthenticated(true);

            setAuthLoading(false);
          }}
        />
        <Toasts toasts={toasts} onDismiss={dismiss} />
      </>
    );
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <div>
          <p className="eyebrow">Clinical workspace</p>
          <h1>Nightingale</h1>
        </div>
        <div className="topbar-actions">
          <span>{user?.email}</span>
          <button onClick={logout}>Log out</button>
        </div>
      </header>

      <VitalsTrace active={requestsInFlight > 0} />

      <nav className="mobile-tabs">
        <button
          className={mobilePanel === "patients" ? "active" : ""}
          onClick={() => setMobilePanel("patients")}
        >
          <IconPanelLeft /> Patients
        </button>
        <button
          className={mobilePanel === "conversation" ? "active" : ""}
          onClick={() => setMobilePanel("conversation")}
        >
          Conversation
        </button>
        <button
          className={mobilePanel === "context" ? "active" : ""}
          onClick={() => setMobilePanel("context")}
        >
          <IconPanelRight /> Context
        </button>
      </nav>

      <section className={`workspace panel-focus-${mobilePanel}`}>
        <PatientsPanel
          records={records}
          recordsLoading={recordsLoading}
          selectedRecordId={selectedRecordId}
          onSelectRecord={(id) => {
            selectRecord(id);
            setMobilePanel("conversation");
          }}
          onCreatePatient={createPatient}
          onUpdatePatient={updatePatient}
          onDeletePatient={deletePatient}
        />

        <ConversationPanel
          selectedRecord={selectedRecord}
          sessions={patientSessions}
          selectedSessionId={selectedSessionId}
          selectedSession={selectedSession}
          onSelectSession={(id) => setSelectedSessionId(String(id))}
          onNewConversation={newConversation}
          onDeleteSession={deleteSession}
          messages={messages}
          messagesLoading={messagesLoading}
          historyUnavailable={historyUnavailable}
          chatInput={chatInput}
          setChatInput={setChatInput}
          onSubmitMessage={(text) => sendMessage(text)}
          isSending={isSending}
        />

        <ContextPanel
          selectedRecord={selectedRecord}
          documents={documents}
          documentsLoading={documentsLoading}
          onUploadFiles={uploadFiles}
          onOpenDocument={setViewerDocument}
          searchQuery={searchQuery}
          setSearchQuery={setSearchQuery}
          onSearch={searchDocuments}
          searchResults={searchResults}
          searching={searching}
          lastSources={lastSources}
          lastSuggestedQuestions={lastSuggestedQuestions}
          onAskSuggested={(q) => sendMessage(q)}
          reportSummary={reportSummary}
        />
      </section>

      {viewerDocument && (
        <DocumentViewerModal
          document={viewerDocument}
          onClose={() => setViewerDocument(null)}
          onDelete={deleteDocument}
          runAction={withTracking}
        />
      )}

      <Toasts toasts={toasts} onDismiss={dismiss} />
    </main>
  );
}
