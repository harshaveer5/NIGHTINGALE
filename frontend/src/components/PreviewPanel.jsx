import React from "react";

export default function PreviewPanel({ selectedDocument, previewUrl, ocrText }) {
  return (
    <section className="panel preview-panel">
      <div className="panel-header">
        <h2>Preview</h2>
        {selectedDocument && <span>Document #{selectedDocument.id}</span>}
      </div>
      {selectedDocument ? (
        <>
          {previewUrl ? (
            <iframe title="Document preview" src={previewUrl} />
          ) : (
            <p className="muted">Loading preview…</p>
          )}
          <details>
            <summary>Extracted text</summary>
            <pre>{ocrText || "Open OCR on a document to load its extracted text."}</pre>
          </details>
        </>
      ) : (
        <div className="empty-state">Select a document from the list to preview it here.</div>
      )}
    </section>
  );
}
