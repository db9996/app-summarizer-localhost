import { useState } from "react";
import api from "../api/axios"; // Only use this!

function Summarizer() {
  const [textOrUrl, setTextOrUrl] = useState("");
  const [summary, setSummary] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  // Poll status using api—you do NOT need the token in headers, api interceptor handles JWT
  const pollTaskStatus = async (taskId) => {
    let done = false;
    let response = null;
    while (!done) {
      await new Promise((res) => setTimeout(res, 1500));
      try {
        response = await api.get(`/task/${taskId}`);
        if (response.data.state === "SUCCESS") {
          done = true;
        } else if (response.data.state === "FAILURE") {
          setError("Summarization failed");
          done = true;
        }
      } catch (pollError) {
        setError("Failed to get summary status");
        done = true;
      }
    }
    return response?.data?.summary || "";
  };

  // Submission uses api, no manual JWT header needed
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSummary("");
    setError("");
    setLoading(true);
    try {
      const response = await api.post("/api/summarize", { text: textOrUrl });
      const taskId = response.data.task_id;
      const finalSummary = await pollTaskStatus(taskId);
      setSummary(finalSummary);
    } catch (err) {
      setError(err.response?.data?.msg || "Failed to summarize");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="summarizer-container">
      <h2 className="summarizer-title">Summarizer</h2>
      <form className="summarizer-form" onSubmit={handleSubmit} autoComplete="off">
        <textarea
          className="summarizer-input"
          placeholder="Paste URL or text here"
          value={textOrUrl}
          onChange={e => setTextOrUrl(e.target.value)}
          required
          rows={8}
        />
        <button type="submit" disabled={loading}>
          Summarize
        </button>
      </form>
      {loading && <p className="summarizer-loading">Summarizing, please wait...</p>}
      {summary && (
        <div className="summarizer-summary">
          <h3>Summary:</h3>
          <p>{summary}</p>
        </div>
      )}
      {error && <p className="summarizer-error">{error}</p>}
    </div>
  );
}

export default Summarizer;
