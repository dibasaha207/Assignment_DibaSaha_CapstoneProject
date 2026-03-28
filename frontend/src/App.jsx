import { useCallback, useState } from "react";
import "./App.css";

const API_BASE = import.meta.env.VITE_API_URL || "";

function apiUrl(path) {
  if (API_BASE) return `${API_BASE.replace(/\/$/, "")}${path}`;
  return `/api${path}`;
}

export default function App() {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [result, setResult] = useState(null);

  const analyze = useCallback(async () => {
    setError(null);
    setResult(null);
    const trimmed = text.trim();
    if (!trimmed) {
      setError("Paste a message to analyze.");
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(apiUrl("/predict"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: trimmed }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        const d = data.detail;
        const msg =
          typeof d === "string"
            ? d
            : Array.isArray(d)
              ? d.map((x) => x.msg || x).join(" ")
              : res.statusText;
        throw new Error(msg || "Request failed");
      }
      setResult(data);
    } catch (e) {
      setError(e.message || "Could not reach the API. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [text]);

  return (
    <div className="page">
      <header className="hero">
        <p className="eyebrow">AI Capstone · SpamGuard</p>
        <h1>Spot risky texts before you reply</h1>
        <p className="lede">
          Paste an SMS, chat snippet, or email body. A <strong>Multinomial Naive Bayes</strong> model
          trained on the UCI SMS Spam Collection estimates spam probability and offers practical safety
          tips.
        </p>
      </header>

      <main className="grid">
        <section className="card input-card">
          <label htmlFor="msg">Message to analyze</label>
          <textarea
            id="msg"
            rows={8}
            placeholder="e.g. Congratulations! You've won $1000. Click here to claim..."
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={loading}
          />
          <div className="actions">
            <button type="button" className="primary" onClick={analyze} disabled={loading}>
              {loading ? "Analyzing…" : "Run AI check"}
            </button>
            <button
              type="button"
              className="ghost"
              onClick={() => {
                setText("");
                setResult(null);
                setError(null);
              }}
              disabled={loading}
            >
              Clear
            </button>
          </div>
          {error && <p className="err">{error}</p>}
        </section>

        <section className="card result-card">
          <h2>Result</h2>
          {!result && !loading && (
            <p className="placeholder">Your prediction and guidance will appear here.</p>
          )}
          {loading && <p className="placeholder pulse">Calling the model…</p>}
          {result && (
            <div className="outcome">
              <div className={`badge ${result.label === "spam" ? "bad" : "ok"}`}>
                {result.label === "spam" ? "Likely spam" : "Likely legitimate"}
              </div>
              <div className="meters">
                <div className="meter">
                  <span>Spam probability</span>
                  <div className="bar-wrap">
                    <div
                      className="bar spam"
                      style={{ width: `${Math.round(result.spam_probability * 100)}%` }}
                    />
                  </div>
                  <strong>{(result.spam_probability * 100).toFixed(1)}%</strong>
                </div>
                <div className="meter">
                  <span>Legitimate probability</span>
                  <div className="bar-wrap">
                    <div
                      className="bar ham"
                      style={{ width: `${Math.round(result.ham_probability * 100)}%` }}
                    />
                  </div>
                  <strong>{(result.ham_probability * 100).toFixed(1)}%</strong>
                </div>
              </div>
              <p className="advice">{result.advice}</p>
            </div>
          )}
          <p className="disclaimer">
            Educational prototype — not a guarantee. When in doubt, verify through official channels
            and never share OTPs or passwords.
          </p>
        </section>
      </main>

      <footer className="foot">
        <span>Backend: Starlette · Model: NB + UCI dataset</span>
      </footer>
    </div>
  );
}
