import React, { useId } from "react";

const PATH_D =
  "M0,17 L120,17 L136,17 L146,3 L158,31 L170,17 L184,17 L196,9 L204,17 L900,17";

export default function VitalsTrace({ active }) {
  const gradientId = useId();

  return (
    <div className={`vitals-trace${active ? " active" : ""}`} aria-hidden="true">
      <svg viewBox="0 0 900 34" preserveAspectRatio="none">
        <defs>
          <linearGradient id={gradientId} x1="0" x2="1" y1="0" y2="0">
            <stop offset="0%" stopColor="var(--teal)" stopOpacity="0" />
            <stop offset="50%" stopColor="var(--teal)" stopOpacity="1" />
            <stop offset="100%" stopColor="var(--teal)" stopOpacity="0" />
          </linearGradient>
        </defs>
        <path d={PATH_D} fill="none" strokeWidth="1.5" />
        <path
          d={PATH_D}
          fill="none"
          strokeWidth="2"
          stroke={`url(#${gradientId})`}
          strokeDasharray="220 1400"
          className="pulse-dot"
          style={{ animationDuration: active ? "0.9s" : "3.2s" }}
        />
      </svg>
    </div>
  );
}
