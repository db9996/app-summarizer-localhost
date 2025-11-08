import { useState } from "react";
import api from "../api/axios";

const GOOGLE_AUTH_URL = "https://app-backend1.onrender.com/api/oauth/google/google";


function Login({ onLogin, goToSignup }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    if (!username || !password) {
      setError("Missing username or password");
      return;
    }
    try {
      const response = await api.post("/login", {
        username,
        password,
      });
      const token = response.data.token;
      localStorage.setItem("token", token);
      alert("Login successful! JWT saved.");
      if (onLogin) onLogin(token);
    } catch (err) {
      setError(err.response?.data?.msg || "Login failed");
    }
  };

  return (
    <div className="card">
      <div className="login-header" style={{ textAlign: "center", marginBottom: "1em" }}>
        <h1 style={{ fontSize: "2em", fontWeight: 700 }}>Sign In</h1>
        <p style={{ color: "#6b7280" }}>Welcome back! Please enter your credentials.</p>
      </div>

      <div className="login-oauth" style={{ display: "flex", flexDirection: "column", gap: "0.75rem", marginBottom: "1em" }}>
        <a
          href={GOOGLE_AUTH_URL}
          style={{
            background: "#4285f4",
            color: "white",
            fontWeight: 600,
            borderRadius: "0.375rem",
            padding: "0.75rem 1rem",
            fontSize: "1.05rem",
            textAlign: "center",
            cursor: "pointer",
            textDecoration: "none",
          }}
        >
          Sign in with Google
        </a>
      </div>

      <div className="login-div" style={{ display: "flex", alignItems: "center", marginBottom: ".6em", color: "#6b7280", fontSize: "0.98em" }}>
        <hr style={{ flexGrow: 1, border: "none", borderTop: "1px solid #d1d5db" }} />
        <span style={{ margin: "0 0.8em" }}>or</span>
        <hr style={{ flexGrow: 1, border: "none", borderTop: "1px solid #d1d5db" }} />
      </div>

      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1em" }}>
        <div>
          <label htmlFor="username">Username</label>
          <input
            id="username"
            name="username"
            type="text"
            required
            value={username}
            onChange={e => setUsername(e.target.value)}
            autoComplete="username"
            placeholder="Your username"
            style={{ width: "100%", padding: "0.7em", fontSize: "1em", borderRadius: "0.5rem", border: "1px solid #d1d5db" }}
          />
        </div>
        <div>
          <label htmlFor="email">Email address</label>
          <input
            id="email"
            name="email"
            type="email"
            required
            value={email}
            onChange={e => setEmail(e.target.value)}
            autoComplete="email"
            placeholder="you@example.com"
            style={{ width: "100%", padding: "0.7em", fontSize: "1em", borderRadius: "0.5rem", border: "1px solid #d1d5db" }}
          />
        </div>
        <div>
          <label htmlFor="password">Password</label>
          <input
            id="password"
            name="password"
            type="password"
            required
            value={password}
            onChange={e => setPassword(e.target.value)}
            autoComplete="current-password"
            placeholder="••••••••"
            style={{ width: "100%", padding: "0.7em", fontSize: "1em", borderRadius: "0.5rem", border: "1px solid #d1d5db" }}
          />
        </div>
        <button
          type="submit"
          style={{
            width: "100%",
            background: "#2563eb",
            color: "#fff",
            fontWeight: 600,
            padding: "0.75em",
            borderRadius: "0.6em",
            border: "none",
            margin: "8px 0",
            fontSize: "1em",
            cursor: "pointer",
          }}
        >
          Sign In
        </button>
      </form>

      {error && (
        <div
          style={{
            color: "#dc2626",
            background: "#fef2f2",
            borderRadius: "0.5em",
            padding: "8px",
            marginBottom: "8px",
            textAlign: "center",
          }}
        >
          {error}
        </div>
      )}

      <div style={{ textAlign: "center", color: "#6b7280", fontSize: "1em", marginTop: "1.5em" }}>
        Don't have an account?{" "}
        <button
          type="button"
          onClick={goToSignup}
          style={{
            color: "#2563eb",
            background: "none",
            border: "none",
            cursor: "pointer",
            textDecoration: "underline",
            fontWeight: "bold",
          }}
        >
          Sign up
        </button>
      </div>
    </div>
  );
}

export default Login;
