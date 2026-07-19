import React from "react";

export function SkeletonLine({ width = "100%" }) {
  return <span className="skeleton-line" style={{ width }} />;
}

export function SkeletonCard() {
  return (
    <div className="skeleton-card">
      <SkeletonLine width="55%" />
      <SkeletonLine width="35%" />
    </div>
  );
}

export function SkeletonMessage({ align = "left" }) {
  return (
    <div className={`skeleton-message ${align}`}>
      <SkeletonLine width="70%" />
      <SkeletonLine width="45%" />
    </div>
  );
}
