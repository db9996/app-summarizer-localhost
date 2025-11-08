import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

function History() {
  const [summaries, setSummaries] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [authChecked, setAuthChecked] = useState(false);
  const navigate = useNavigate();

  // Robust session check with REPLACE
  useEffect(() => {
    let cancelled = false;
    api.get("/whoami")
      .then(() => setAuthChecked(true))
      .catch(() => {
        setError("Session expired. Redirecting to login…");
        setTimeout(() => {
          if (!cancelled) navigate("/login", { replace: true });
        }, 1500);
      });
    return () => { cancelled = true; };
  }, [navigate]);

  useEffect(() => {
    if (!authChecked) return;
    const fetchSummaries = async () => {
      setLoading(true);
      setError("");
      try {
        const response = await api.get("https://app-backend1.onrender.com/api/summaries"); // Always GET
        setSummaries(response.data);
      } catch (err) {
        setError(err.response?.data?.msg || "Failed to load summaries.");
      }
      setLoading(false);
    };
    fetchSummaries();
  }, [authChecked]);

  const handleDelete = async (id) => {
    if (window.confirm("Delete this summary?")) {
      try {
        await api.delete(`/summary/${id}`);
        setSummaries(summaries.filter(s => s.id !== id));
      } catch (err) {
        setError("Failed to delete summary.");
      }
    }
  };

  if (!authChecked) {
    return (
      <div className="text-center">
        {error || "Checking session…"}
        {error && (
          <div>
            <button onClick={() => navigate("/login", { replace: true })}>Go to Login</button>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto p-6 bg-white rounded shadow mt-8">
      <h2 className="text-3xl font-bold mb- text-center">Summary History</h2>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-500">{error}</p>}
      {(!loading && summaries.length === 0) && <p>No summaries found.</p>}
      <ul className="history-list">
        {summaries.filter(s => s.summary).map((s) => (
          <li key={s.id} className="history-item">
            <div className="history-id">Summary #{s.id}</div>
            <div className="history-summary">{s.summary ? s.summary : <i>Summary pending...</i>}</div>
            {s.created_at && (
              <div className="history-date">Created at: {new Date(s.created_at).toLocaleString()}</div>
            )}
            <button
              className="history-delete-btn"
              onClick={() => handleDelete(s.id)}
            >
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default History;
