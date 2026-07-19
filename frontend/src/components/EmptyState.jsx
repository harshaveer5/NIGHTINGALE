import React from "react";

export default function EmptyState({ icon, title, hint, action }) {
  return (
    <div className="empty-state">
      {icon && <div className="empty-state-icon">{icon}</div>}
      {title && <p className="empty-state-title">{title}</p>}
      {hint && <p className="muted">{hint}</p>}
      {action}
    </div>
  );
}
