import React, { useEffect, useRef, useState } from "react";
import { IconChevronDown, IconHistory, IconPlus, IconTrash } from "./Icons";

function formatWhen(isoString) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "";
  const now = new Date();
  const sameDay = date.toDateString() === now.toDateString();
  return sameDay
    ? date.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" })
    : date.toLocaleDateString([], { month: "short", day: "numeric" });
}

export default function ConversationHistoryMenu({
  sessions,
  selectedSessionId,
  onSelectSession,
  onDeleteSession,
  onNewConversation,
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function handleClickOutside(event) {
      if (ref.current && !ref.current.contains(event.target)) setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const activeSession = sessions.find((s) => String(s.id) === String(selectedSessionId));

  return (
    <div className="history-menu" ref={ref}>
      <button className="ghost icon-button" onClick={() => setOpen((v) => !v)}>
        <IconHistory />
        {activeSession ? activeSession.title : "History"}
        <IconChevronDown />
      </button>

      {open && (
        <div className="history-popover">
          <button
            className="primary history-new"
            onClick={() => {
              onNewConversation();
              setOpen(false);
            }}
          >
            <IconPlus /> New conversation
          </button>

          {sessions.length === 0 ? (
            <p className="muted history-empty">No conversations with this patient yet.</p>
          ) : (
            <ul className="history-list">
              {sessions.map((session) => (
                <li key={session.id}>
                  <button
                    className={`history-item${String(session.id) === String(selectedSessionId) ? " active" : ""}`}
                    onClick={() => {
                      onSelectSession(session.id);
                      setOpen(false);
                    }}
                  >
                    <span className="history-item-title">{session.title}</span>
                    <span className="history-item-when">{formatWhen(session.created_at)}</span>
                  </button>
                  <button
                    className="ghost icon-button history-delete"
                    aria-label={`Delete conversation ${session.title}`}
                    onClick={() => {
                      if (window.confirm(`Delete "${session.title}"?`)) {
                        onDeleteSession(session.id);
                      }
                    }}
                  >
                    <IconTrash />
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
