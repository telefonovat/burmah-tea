// Pixel sprites on a 12×12 grid, crisp edges — the only icon language in the
// app. Everything else stays smooth; the chunky/smooth contrast is the charm.

export function PixelTeaGlass({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 12 12" shapeRendering="crispEdges" className={className} aria-hidden="true">
      {/* steam */}
      <rect x="4" y="1" width="1" height="1" fill="var(--muted)" opacity="0.6" />
      <rect x="6" y="0" width="1" height="1" fill="var(--muted)" opacity="0.6" />
      <rect x="8" y="1" width="1" height="1" fill="var(--muted)" opacity="0.6" />
      {/* glass */}
      <rect x="2" y="3" width="8" height="1" fill="var(--muted)" />
      <rect x="2" y="4" width="1" height="7" fill="var(--muted)" />
      <rect x="9" y="4" width="1" height="7" fill="var(--muted)" />
      <rect x="2" y="11" width="8" height="1" fill="var(--muted)" />
      {/* tea layer, condensed milk below */}
      <rect x="3" y="4" width="6" height="4" fill="var(--accent)" />
      <rect x="3" y="8" width="6" height="3" fill="var(--text)" />
    </svg>
  );
}

export function PixelNewspaper({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 12 12" shapeRendering="crispEdges" className={className} aria-hidden="true">
      {/* folded paper */}
      <rect x="1" y="2" width="10" height="8" fill="var(--text)" />
      {/* masthead */}
      <rect x="2" y="3" width="8" height="2" fill="var(--accent)" />
      {/* text lines */}
      <rect x="2" y="6" width="8" height="1" fill="var(--muted)" />
      <rect x="2" y="8" width="5" height="1" fill="var(--muted)" />
    </svg>
  );
}

/* Tea-stain ring: a glass left on the table. Sits behind the wordmark. */
export function PixelStain({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 12 12" shapeRendering="crispEdges" className={className} aria-hidden="true">
      <g fill="var(--accent)">
        <rect x="4" y="0" width="4" height="1" />
        <rect x="4" y="11" width="4" height="1" />
        <rect x="0" y="4" width="1" height="4" />
        <rect x="11" y="4" width="1" height="4" />
        <rect x="2" y="2" width="1" height="1" />
        <rect x="9" y="2" width="1" height="1" />
        <rect x="2" y="9" width="1" height="1" />
        <rect x="9" y="9" width="1" height="1" />
      </g>
    </svg>
  );
}


