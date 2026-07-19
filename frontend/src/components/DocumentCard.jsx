import React from "react";
import { IconFile, IconImage } from "./Icons";

function isImage(document) {
  return /\.(png|jpe?g)$/i.test(document.filename) || document.file_type?.startsWith("image/");
}

export default function DocumentCard({ document, onOpen }) {
  return (
    <button className="document-card" onClick={() => onOpen(document)}>
      <span className="document-card-icon">
        {isImage(document) ? <IconImage /> : <IconFile />}
      </span>
      <span className="document-card-body">
        <span className="document-card-name">{document.filename}</span>
        <span className="document-card-meta">
          {document.document_type || "Unclassified"}
          {document.report_date ? ` · ${document.report_date}` : ""}
        </span>
      </span>
    </button>
  );
}
