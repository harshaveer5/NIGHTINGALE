import React, { useEffect, useRef } from "react";

function Message({ message }) {
  const payload = message.payload;

  return (
    <article className={`message ${message.role}`}>
      <div className="message-content">{message.content}</div>

      {payload && (
        <div className="message-meta">
          {payload.intent && <span>{payload.intent}</span>}
          {typeof payload.processing_time_ms === "number" && (
            <span>{payload.processing_time_ms} ms</span>
          )}
          {payload.response_source && <span>{payload.response_source}</span>}
        </div>
      )}

      {payload?.sources?.length > 0 && (
        <details>
          <summary>Sources ({payload.sources.length})</summary>
          <ul>
            {payload.sources.map((source, index) => (
              <li key={`${source.document_id}-${source.chunk_index}-${index}`}>
                {source.filename} · chunk {source.chunk_index}
              </li>
            ))}
          </ul>
        </details>
      )}

      {payload?.latency_trace?.stages?.length > 0 && (
        <details>
          <summary>Latency trace</summary>
          <div className="trace-list">
            {payload.latency_trace.stages.map((stage, index) => (
              <div key={`${stage.name}-${index}`}>
                <span>{stage.name}</span>
                <strong>{stage.duration_ms} ms</strong>
              </div>
            ))}
          </div>
        </details>
      )}
    </article>
  );
}

export default function ChatPanel({
  selectedRecord,
  messages,
  chatInput,
  setChatInput,
  onSend,
  isSending,
  canChat,
}) {
  const listRef = useRef(null);

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages.length]);

  return (
    <section className="panel chat-panel">
      <div className="panel-header">
        <h2>Chat</h2>
        <span>{selectedRecord?.patient_name || "No patient selected"}</span>
      </div>

      <div className="messages" ref={listRef}>
        {messages.length === 0 && (
          <p className="muted">
            Try: "What reports do I have?" or "Compare the two CBC reports."
          </p>
        )}
        {messages.map((message, index) => (
          <Message key={`${message.role}-${index}`} message={message} />
        ))}
      </div>

      <form onSubmit={onSend} className="chat-input">
        <input
          value={chatInput}
          onChange={(event) => setChatInput(event.target.value)}
          placeholder="Ask about reports, labs, medicines, or comparisons"
          disabled={!canChat || isSending}
          aria-label="Ask the assistant a question"
        />
        <button className="primary" type="submit" disabled={!canChat || isSending || !chatInput.trim()}>
          {isSending ? "Sending…" : "Send"}
        </button>
      </form>
    </section>
  );
}
