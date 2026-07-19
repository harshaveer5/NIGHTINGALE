import React, { useEffect, useRef } from "react";
import { IconSend } from "./Icons";

export default function ComposerInput({ value, onChange, onSubmit, disabled, placeholder }) {
  const textareaRef = useRef(null);

  useEffect(() => {
    const el = textareaRef.current;
    if (!el) return;
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }, [value]);

  function handleKeyDown(event) {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      onSubmit();
    }
  }

  return (
    <form
      className="chat-input"
      onSubmit={(event) => {
        event.preventDefault();
        onSubmit();
      }}
    >
      <textarea
        ref={textareaRef}
        value={value}
        onChange={(event) => onChange(event.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholder}
        disabled={disabled}
        rows={1}
        aria-label="Ask the assistant a question"
      />
      <button className="primary icon-button" type="submit" disabled={disabled || !value.trim()}>
        <IconSend />
        <span className="sr-only-inline">Send</span>
      </button>
    </form>
  );
}
