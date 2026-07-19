import React, { useState } from "react";
import DocumentCard from "./DocumentCard";
import UploadDropzone from "./UploadDropzone";
import EmptyState from "./EmptyState";
import { SkeletonCard } from "./Skeleton";
import { IconSearch, IconFile, IconSparkle, IconUser } from "./Icons";

const TABS = [
  { id: "documents", label: "Documents" },
  { id: "insights", label: "Insights" },
  { id: "reference", label: "Reference" },
];

export default function ContextPanel({
  selectedRecord,
  documents,
  documentsLoading,
  onUploadFiles,
  onOpenDocument,
  searchQuery,
  setSearchQuery,
  onSearch,
  searchResults,
  searching,
  lastSources,
  lastSuggestedQuestions,
  onAskSuggested,
  reportSummary,
}) {
  const [tab, setTab] = useState("documents");
  const [showSearch, setShowSearch] = useState(false);

  if (!selectedRecord) {
    return (
      <aside className="context-panel">
        <EmptyState
          icon={<IconFile />}
          title="No patient selected"
          hint="Choose a patient on the left to see their documents and context here."
        />
      </aside>
    );
  }

  const hasInsights = lastSources.length > 0 || Boolean(reportSummary) || lastSuggestedQuestions?.length > 0;

  return (
    <aside className="context-panel">
      <div className="tab-bar" role="tablist" aria-label="Patient context">
        {TABS.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            className={`tab-button${tab === t.id ? " active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
            {t.id === "insights" && hasInsights && <span className="tab-dot" aria-hidden="true" />}
          </button>
        ))}
      </div>

      {tab === "documents" && (
        <div className="tab-panel" role="tabpanel">
          <div className="panel-header">
            <h2 className="sr-only-inline">Documents</h2>
            <span className="muted">{documents.length} on file</span>
            <button className="ghost icon-button" onClick={() => setShowSearch((v) => !v)}>
              <IconSearch /> {showSearch ? "Hide search" : "Search"}
            </button>
          </div>

          {showSearch && (
            <form
              onSubmit={onSearch}
              className="search-row"
              aria-label="Search this patient's documents"
            >
              <input
                value={searchQuery}
                onChange={(event) => setSearchQuery(event.target.value)}
                placeholder="Search reports, labs, medicines…"
              />
              <button className="primary" type="submit" disabled={searching}>
                {searching ? "…" : "Go"}
              </button>
            </form>
          )}

          {showSearch && searchResults.length > 0 && (
            <div className="search-results">
              {searchResults.map((chunk) => (
                <article key={chunk.chunk_id}>
                  <strong>{chunk.filename}</strong>
                  <span>
                    Chunk {chunk.chunk_index} · score {Number(chunk.score).toFixed(3)}
                  </span>
                  <p>{chunk.chunk_text}</p>
                </article>
              ))}
            </div>
          )}

          <UploadDropzone disabled={!selectedRecord} onFiles={onUploadFiles} />

          {documentsLoading ? (
            <div className="document-card-list">
              <SkeletonCard />
              <SkeletonCard />
              <SkeletonCard />
            </div>
          ) : documents.length === 0 ? (
            <EmptyState hint="No documents yet. Drop a file above to get started." />
          ) : (
            <div className="document-card-list">
              {documents.map((document) => (
                <DocumentCard key={document.id} document={document} onOpen={onOpenDocument} />
              ))}
            </div>
          )}
        </div>
      )}

      {tab === "insights" && (
        <div className="tab-panel" role="tabpanel">
          <div className="insight-block">
            <p className="eyebrow">Report summary</p>
            {reportSummary ? (
              <p className="context-text">{reportSummary}</p>
            ) : (
              <EmptyState
                icon={<IconSparkle />}
                hint="Ask the assistant to summarize a report — the answer pins here."
              />
            )}
          </div>

          <div className="insight-block">
            <p className="eyebrow">Sources</p>
            {lastSources.length === 0 ? (
              <p className="muted">Sources cited in the assistant's last answer will appear here.</p>
            ) : (
              <ul className="source-list">
                {lastSources.map((source, index) => (
                  <li key={`${source.document_id}-${source.chunk_index}-${index}`}>
                    {source.filename} · chunk {source.chunk_index}
                  </li>
                ))}
              </ul>
            )}
          </div>

          {lastSuggestedQuestions?.length > 0 && (
            <div className="insight-block">
              <p className="eyebrow">Follow up</p>
              <div className="suggested-questions">
                {lastSuggestedQuestions.map((question) => (
                  <button key={question} onClick={() => onAskSuggested(question)}>
                    {question}
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {tab === "reference" && (
        <div className="tab-panel" role="tabpanel">
          <div className="insight-block">
            <p className="eyebrow">
              <IconUser /> Patient
            </p>
            <p className="context-text">
              {selectedRecord.patient_name} · {selectedRecord.age} yrs · {selectedRecord.gender}
            </p>
          </div>
          <div className="insight-block">
            <p className="eyebrow">Medical history</p>
            <p className="context-text">
              {selectedRecord.medical_history || "No history on file for this patient."}
            </p>
          </div>
        </div>
      )}
    </aside>
  );
}
