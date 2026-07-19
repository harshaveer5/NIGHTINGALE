import React, { useEffect, useRef, useState } from "react";
import ConversationHistoryMenu from "./ConversationHistoryMenu";
import ComposerInput from "./ComposerInput";
import { SkeletonMessage } from "./Skeleton";
import EmptyState from "./EmptyState";

const prefersReducedMotion =
  typeof window !== "undefined" &&
  window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;

function RevealedText({ text, reveal }) {
  const [shown, setShown] = useState(reveal && !prefersReducedMotion ? "" : text);

  useEffect(() => {
    if (!reveal || prefersReducedMotion) {
      setShown(text);
      return;
    }
    setShown("");
    let i = 0;
    const step = Math.max(1, Math.round(text.length / 120));
    const id = setInterval(() => {
      i += step;
      setShown(text.slice(0, i));
      if (i >= text.length) clearInterval(id);
    }, 12);
    return () => clearInterval(id);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [text]);

  return <span>{shown}</span>;
}

function Message({ message, reveal }) {
  const payload = message.payload;

  return (
    <article className={`message ${message.role}`}>
      <div className="message-content">
        {message.role === "assistant" ? <RevealedText text={message.content} reveal={reveal} /> : message.content}
      </div>

      {payload && (
        <div className="message-meta">
          {payload.intent && <span>{payload.intent}</span>}
          {typeof payload.confidence === "number" && (
            <span>confidence {(payload.confidence * 100).toFixed(0)}%</span>
          )}
          {typeof payload.processing_time_ms === "number" && (
            <span>{payload.processing_time_ms} ms</span>
          )}
          {payload.response_source && <span>{payload.response_source}</span>}
        </div>
      )}

      {payload?.warning && <p className="message-warning">{payload.warning}</p>}

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

export default function ConversationPanel({
  selectedRecord,
  sessions,
  selectedSessionId,
  selectedSession,
  onSelectSession,
  onNewConversation,
  onDeleteSession,
  messages,
  messagesLoading,
  historyUnavailable,
  chatInput,
  setChatInput,
  onSubmitMessage,
  isSending,
}) {
  const listRef = useRef(null);
  const lastAssistantIndex = [...messages].reverse().findIndex((m) => m.role === "assistant");
  const lastAssistantAbsoluteIndex =
    lastAssistantIndex === -1 ? -1 : messages.length - 1 - lastAssistantIndex;

  useEffect(() => {
    if (listRef.current) {
      listRef.current.scrollTop = listRef.current.scrollHeight;
    }
  }, [messages.length]);

  if (!selectedRecord) {
    return (
      <section className="conversation-panel">
        <EmptyState
          title="Select a patient to start"
          hint="Pick a patient on the left, or add a new one, to open their conversation."
        />
      </section>
    );
  }

  const starterPrompts = [
    "What reports do I have on file?",
    "Summarize the most recent report.",
    "Are there any abnormal values I should know about?",
  ];

  return (
    <section className="conversation-panel">
      <div className="conversation-header">
        <div>
          <p className="eyebrow">{selectedRecord.patient_name}</p>
          <h2>{selectedSession ? selectedSession.title : "New conversation"}</h2>
        </div>
        <ConversationHistoryMenu
          sessions={sessions}
          selectedSessionId={selectedSessionId}
          onSelectSession={onSelectSession}
          onDeleteSession={onDeleteSession}
          onNewConversation={onNewConversation}
        />
      </div>

      <div className="messages" ref={listRef}>
        {messagesLoading ? (
          <>
            <SkeletonMessage align="left" />
            <SkeletonMessage align="right" />
          </>
        ) : messages.length === 0 ? (
          <div className="conversation-starter">
            <p className="conversation-starter-title">
              Ask anything about {selectedRecord.patient_name}'s records
            </p>
            <div className="starter-prompts">
              {starterPrompts.map((prompt) => (
                <button key={prompt} onClick={() => onSubmitMessage(prompt)}>
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        ) : (
          <>
            {historyUnavailable && (
              <p className="muted history-note">
                Earlier messages in this conversation aren't available to redisplay yet —
                showing new messages from here forward.
              </p>
            )}
            {messages.map((message, index) => (
              <Message
                key={`${message.role}-${index}`}
                message={message}
                reveal={index === lastAssistantAbsoluteIndex && message.isNew}
              />
            ))}
          </>
        )}
      </div>

      <ComposerInput
        value={chatInput}
        onChange={setChatInput}
        onSubmit={() => onSubmitMessage(chatInput)}
        disabled={isSending}
        placeholder="Ask about reports, labs, medicines, or comparisons"
      />
    </section>
  );
}
