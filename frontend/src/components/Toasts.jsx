import React from "react";
import { IconX } from "./Icons";

export default function Toasts({ toasts, onDismiss }) {
  if (toasts.length === 0) return null;

  return (
    <div className="toast-stack" role="status" aria-live="polite">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast toast-${toast.type}`}>
          <span>{toast.message}</span>
          <button className="ghost icon-button" onClick={() => onDismiss(toast.id)} aria-label="Dismiss notification">
            <IconX />
          </button>
        </div>
      ))}
    </div>
  );
}
