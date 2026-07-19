import React, { useEffect, useRef, useState } from "react";
import { api } from "../api";
import { IconDownload, IconLink, IconScan, IconTrash, IconX } from "./Icons";

export default function DocumentViewerModal({ document, onClose, onDelete, runAction }) {
  const [previewUrl, setPreviewUrl] = useState("");
  const [ocrText, setOcrText] = useState(null);
  const [loadingOcr, setLoadingOcr] = useState(false);
  const closeButtonRef = useRef(null);

  useEffect(() => {
    closeButtonRef.current?.focus();

    function handleKeyDown(event) {
      if (event.key === "Escape") onClose();
    }
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  useEffect(() => {
    let objectUrl = "";
    runAction("Load preview", () => api.getDocumentFileBlob(document.id), { silent: true })
      .then((blob) => {
        objectUrl = URL.createObjectURL(blob);
        setPreviewUrl(objectUrl);
      })
      .catch(() => {});
    return () => {
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [document.id]);

  async function loadOcr() {
    setLoadingOcr(true);
    try {
      const result = await runAction("Load extracted text", () => api.getOcrText(document.id), {
        silent: true,
      });
      setOcrText(result.extracted_text || "No text was extracted from this file.");
    } finally {
      setLoadingOcr(false);
    }
  }

  async function download() {
    const blob = await runAction("Download document", () => api.getDocumentDownloadBlob(document.id));
    const url = URL.createObjectURL(blob);
    const link = window.document.createElement("a");
    link.href = url;
    link.download = document.filename;
    link.click();
    URL.revokeObjectURL(url);
  }

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div
        className="modal-panel"
        onClick={(event) => event.stopPropagation()}
        role="dialog"
        aria-modal="true"
        aria-labelledby="modal-doc-title"
      >
        <div className="modal-header">
          <div>
            <p className="eyebrow">
              {document.document_type || "Unclassified"}
              {document.report_date ? ` · ${document.report_date}` : ""}
            </p>
            <h2 id="modal-doc-title">{document.filename}</h2>
          </div>
          <button className="ghost icon-button" onClick={onClose} aria-label="Close preview" ref={closeButtonRef}>
            <IconX />
          </button>
        </div>

        <div className="modal-actions">
          <button onClick={download}>
            <IconDownload /> Download
          </button>
          <button onClick={loadOcr} disabled={loadingOcr}>
            <IconScan /> {loadingOcr ? "Reading…" : "Extract text"}
          </button>
          <button onClick={() => runAction("Embed document", () => api.embedDocument(document.id))}>
            <IconLink /> Embed for search
          </button>
          <button
            className="danger"
            onClick={() => {
              if (window.confirm(`Remove ${document.filename}? This cannot be undone.`)) {
                onDelete(document.id);
                onClose();
              }
            }}
          >
            <IconTrash /> Remove
          </button>
        </div>

        <div className="modal-body">
          {previewUrl ? (
            <iframe title="Document preview" src={previewUrl} />
          ) : (
            <div className="skeleton-card" style={{ height: 320 }} />
          )}

          {ocrText !== null && (
            <details open>
              <summary>Extracted text</summary>
              <pre>{ocrText}</pre>
            </details>
          )}
        </div>
      </div>
    </div>
  );
}
