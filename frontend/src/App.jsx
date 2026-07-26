import { useEffect, useRef, useState } from "react";
import PromptForm from "./components/PromptForm.jsx";
import AgentLog from "./components/AgentLog.jsx";
import Card from "./components/Card.jsx";
import Gallery from "./components/Gallery.jsx";
import { generateCard, fetchGallery } from "./lib/api.js";

const STEP_COUNT = 4; // matches STEP_LABELS in AgentLog.jsx
const STEP_INTERVAL_MS = 550;

export default function App() {
  const [isLoading, setIsLoading] = useState(false);
  const [visibleSteps, setVisibleSteps] = useState(0);
  const [card, setCard] = useState(null);
  const [error, setError] = useState(null);
  const [gallery, setGallery] = useState([]);
  const timerRef = useRef(null);

  useEffect(() => {
    fetchGallery().then(setGallery).catch(() => {});
    return () => clearInterval(timerRef.current);
  }, []);

  async function handleSubmit(prompt) {
    setIsLoading(true);
    setError(null);
    setCard(null);
    setVisibleSteps(0);

    // kick off the real request immediately...
    const requestPromise = generateCard(prompt);

    // ...while the log advances on its own clock, so it feels alive even
    // though the actual work happens in one round trip
    timerRef.current = setInterval(() => {
      setVisibleSteps((n) => Math.min(n + 1, STEP_COUNT - 1));
    }, STEP_INTERVAL_MS);

    try {
      const result = await requestPromise;
      clearInterval(timerRef.current);
      setVisibleSteps(STEP_COUNT); // reveal the final "rendering" line too
      await new Promise((r) => setTimeout(r, STEP_INTERVAL_MS));
      setCard(result);
      setGallery((g) => [result, ...g]);
    } catch (err) {
      clearInterval(timerRef.current);
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="eyebrow">
        <span className="dot" />
        mistral agent · generative render · no image model
      </div>

      <div className="hero">
        <h1>
          Describe <em>your</em> current vibe.
          <br />
          Get an <em>artifact</em>.
        </h1>
        <p>
          A small agent reads what you type, decides on rarity and traits, 
          writes it a name and lore — then a deterministic renderer draws it.
          It could be anything, really :) Same words always draw the same piece.
        </p>
      </div>

      <PromptForm onSubmit={handleSubmit} isLoading={isLoading} />

      {error && <p className="error-message">{error}</p>}

      {isLoading && <AgentLog visibleCount={visibleSteps} />}

      {card && !isLoading && <Card card={card} />}

      <Gallery items={gallery} />
    </div>
  );
}
