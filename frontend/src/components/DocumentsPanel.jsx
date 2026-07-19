import React from "react";
import { IconEye, IconDownload, IconScan, IconLink, IconTrash } from "./Icons";

export default function DocumentsPanel({
  documents,
  selectedRecordId,
  onUpload,
  onSelectDocument,
  onDownload,
  onLoadOcr,
  onEmbed,
  onDelete,
}) {
  return (
    <section className="panel documents-panel">
      <div className="panel-header">
        <h2>Documents</h2>
        <span>{documents.length} files</span>
      </div>

      <form onSubmit={onUpload} className="upload-row">
        <input name="file" type="file" accept=".pdf,.png,.jpg,.jpeg" aria-label="Choose a file to upload" />
        <button className="primary" type="submit" disabled={!selectedRecordId}>
          Upload
        </button>
      </form>

      {documents.length === 0 ? (
        <div className="empty-state">
          {selectedRecordId
            ? "No documents yet. Upload a report or scan to get started."
            : "Select a patient to see their documents."}
        </div>
      ) : (
        <div className="document-list">
          {documents.map((document) => (
            <article key={document.id} className="document-item">
              <button className="link-button" onClick={() => onSelectDocument(document)}>
                {document.filename}
              </button>
              <span>
                {document.document_type || "Unclassified"} · {document.report_date || "No date on file"}
              </span>
              <div className="row-actions">
                <button onClick={() => onSelectDocument(document)}>
                  <IconEye /> Preview
                </button>
                <button onClick={() => onDownload(document)}>
                  <IconDownload /> Download
                </button>
                <button onClick={() => onLoadOcr(document)}>
                  <IconScan /> OCR
                </button>
                <button onClick={() => onEmbed(document.id)}>
                  <IconLink /> Embed
                </button>
                <button
                  className="danger"
                  onClick={() => {
                    if (window.confirm(`Remove ${document.filename}?`)) {
                      onDelete(document.id);
                    }
                  }}
                >
                  <IconTrash /> Remove
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
