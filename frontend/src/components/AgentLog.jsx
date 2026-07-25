const STEP_LABELS = [
  "reading the mood and theme",
  "deciding traits and rarity",
  "writing the lore",
  "rendering the piece",
];

/**
 * The backend answers in one request, so this stagger is simulated on the
 * client (via the `visibleCount` prop the parent advances on a timer) -
 * it's not literally streaming step-by-step, but it's an honest
 * representation of the real sequential work the agent did, just replayed
 * for the person watching instead of shown instantly all at once.
 */
export default function AgentLog({ visibleCount }) {
  return (
    <div className="process-log">
      {STEP_LABELS.map((label, i) => {
        if (i >= visibleCount) return null;
        const isActive = i === visibleCount - 1;
        const isDone = i < visibleCount - 1;
        return (
          <div
            key={label}
            className={`process-log-line ${isDone ? "done" : ""} ${
              isActive ? "active" : ""
            }`}
            style={{ animationDelay: `${i * 0.05}s` }}
          >
            <span className="status">{isDone ? "✓" : "›"}</span>
            <span>
              {label}
              {isActive && <span className="cursor" />}
            </span>
          </div>
        );
      })}
    </div>
  );
}
