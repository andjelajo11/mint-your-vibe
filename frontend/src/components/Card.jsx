import { useState } from "react";

const RARITY_LABELS = {
  common: "Common",
  uncommon: "Uncommon",
  rare: "Rare",
  epic: "Epic",
  legendary: "Legendary",
};

function rarityColorVar(rarity) {
  return `var(--rarity-${rarity || "common"})`;
}

export default function Card({ card }) {
  const [showReasoning, setShowReasoning] = useState(false);
  const { metadata, image_base64, reasoning_hash, steps, prompt } = card;

  const imageSrc = `data:image/png;base64,${image_base64}`;

  function download() {
    const link = document.createElement("a");
    link.href = imageSrc;
    link.download = `${metadata.name.replace(/\s+/g, "-").toLowerCase()}.png`;
    link.click();
  }

  function copyLink() {
    navigator.clipboard.writeText(window.location.href);
  }

  return (
    <div className="result">
      <div className="card">
        <img className="card-art" src={imageSrc} alt={metadata.name} />
        <div className="card-body">
          <div className="card-header">
            <h2>{metadata.name}</h2>
            <span
              className="rarity-badge"
              style={{ color: rarityColorVar(metadata.rarity) }}
            >
              {RARITY_LABELS[metadata.rarity] || metadata.rarity}
            </span>
          </div>
          <p className="card-theme">
            {metadata.theme} · {metadata.mood} · energy {metadata.energy_level}/10
          </p>

          <p className="card-lore">"{metadata.lore}"</p>

          <div className="trait-grid">
            {Object.entries(metadata.traits || {}).map(([key, value]) => (
              <div className="trait-chip" key={key}>
                <span className="label">{key}</span>
                <span className="value">{value}</span>
              </div>
            ))}
          </div>

          <div className="card-actions">
            <button className="btn btn-primary" onClick={download}>
              Download
            </button>
            <button className="btn" onClick={copyLink}>
              Copy link
            </button>
          </div>

          <div className="hash-row" title="SHA-256 of the full agent reasoning trace">
            <span>proof hash</span>
            <span className="hash-value">
              {reasoning_hash.slice(0, 16)}…
            </span>
          </div>

          <button
            className="reasoning-toggle"
            onClick={() => setShowReasoning((s) => !s)}
          >
            {showReasoning ? "▾" : "▸"} how the agent decided this
          </button>

          {showReasoning && (
            <div className="reasoning-panel">
              <span className="step-label">1. analysis</span>
              {JSON.stringify(steps["1_analysis"], null, 2)}
              <span className="step-label">2. traits</span>
              {JSON.stringify(steps["2_traits"], null, 2)}
              <span className="step-label">3. lore</span>
              {JSON.stringify(steps["3_lore"], null, 2)}
              <span className="step-label">from prompt</span>
              "{prompt}"
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
