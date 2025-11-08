import { useState } from "react";
import api from "../api/axios";

const GOOGLE_AUTH_URL = "https://app-backend1.onrender.com/api/oauth/google/google";

function Signup({ onSignup, goToLogin }) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      const response = await api.post("/signup", {
        username,
        email,
        password,
      });
      alert("Signup successful! Please login.");
      if (onSignup) onSignup();
    } catch (err) {
      setError(err.response?.data?.msg || "Signup failed");
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-card">
        <div className="signup-header">
          <h2 className="signup-title">Sign Up</h2>
        </div>
        <div className="signup-oauth">
          <a href={GOOGLE_AUTH_URL} className="google">
            Sign up with Google
          </a>
        </div>
        <div className="signup-div">
          <hr />
          <span>or</span>
          <hr />
        </div>
        <form className="signup-form" onSubmit={handleSubmit}>
          <div>
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={e => setUsername(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              required
            />
          </div>
          <div>
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              required
            />
          </div>
          <button type="submit">Sign Up</button>
          {error && <div className="signup-error">{error}</div>}
        </form>
        <div className="signup-login">
          Already have an account?{" "}
          <button type="button" onClick={goToLogin}>
            Log in
          </button>
        </div>
      </div>
    </div>
  );
}

export default Signup;
