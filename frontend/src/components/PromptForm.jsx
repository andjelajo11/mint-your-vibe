import { useState } from "react";

const EXAMPLES = [
  "a storm rolling over a neon city",
  "quiet morning fog on a mountain lake",
  "static on an old television at 3am",
];

export default function PromptForm({ onSubmit, isLoading }) {
  const [value, setValue] = useState("");

  function handleSubmit(e) {
    e.preventDefault();
    if (!value.trim() || isLoading) return;
    onSubmit(value.trim());
  }

  function useExample(ex) {
    setValue(ex);
  }

  return (
    <div>
      <form className="prompt-form" onSubmit={handleSubmit}>
        <input
          className="prompt-input"
          type="text"
          placeholder="Describe a vibe, a mood, a moment..."
          value={value}
          onChange={(e) => setValue(e.target.value)}
          disabled={isLoading}
          maxLength={200}
        />
        <button className="prompt-submit" type="submit" disabled={isLoading}>
          {isLoading ? "Reading it..." : "Mint it"}
        </button>
      </form>
      <p className="prompt-hint">
        Try:{" "}
        {EXAMPLES.map((ex, i) => (
          <span key={ex}>
            <button
              type="button"
              onClick={() => useExample(ex)}
              style={{
                background: "none",
                border: "none",
                color: "inherit",
                textDecoration: "underline",
                cursor: "pointer",
                padding: 0,
                font: "inherit",
              }}
            >
              {ex}
            </button>
            {i < EXAMPLES.length - 1 ? " · " : ""}
          </span>
        ))}
      </p>
    </div>
  );
}
