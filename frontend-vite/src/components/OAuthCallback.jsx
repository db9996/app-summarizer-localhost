import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";

function OAuthCallback({ onLogin }) {
  const location = useLocation();
  const navigate = useNavigate();
  const [error, setError] = useState(null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true); // For spinner state

  useEffect(() => {
    // --- FIX: Get token from "jwt" query param (matches backend redirect) ---
    const params = new URLSearchParams(location.search);
    const jwtToken = params.get("jwt");
    const errorMsg = params.get("error"); // If backend returns an error

    let errorTimeout;
    // Always check login by calling /api/whoami
    fetch("http://app-backend1.onrender.com/api/whoami", { 
      credentials: "include",
      headers: jwtToken ? { Authorization: `Bearer ${jwtToken}` } : {}
    })
      .then(res => {
        if (!res.ok) throw new Error("Not logged in");
        return res.json();
      })
      .then(data => {
        setUser(data);
        setError(null);
        setLoading(false);
        if (jwtToken) localStorage.setItem("token", jwtToken);
        if (onLogin) onLogin(jwtToken || data);
        // Redirect to main app if you want (remove comment to use)
        // navigate("/summarizer");
      })
      .catch(() => {
        // Delay before showing error to allow cookie/session propagation
        errorTimeout = setTimeout(() => {
          // If not logged in with session, fallback to JWT logic
          if (jwtToken) {
            localStorage.setItem("token", jwtToken);
            if (onLogin) onLogin(jwtToken);
            navigate("/summarizer"); // or "/" if you want
          } else if (errorMsg) {
            setError(errorMsg);
          } else {
            setError("Google login failed. Please try again.");
          }
          setLoading(false);
        }, 1500); // 1.5 seconds
      });
    return () => clearTimeout(errorTimeout);
  }, [location, onLogin, navigate]);

  if (loading) {
    return <div>Signing you in…</div>;
  }

  if (user) {
    return (
      <div>
        <h2>Google Login Successful!</h2>
        <p>Welcome, {user.email}.</p>
        {/* Redirect/navigate, or let user continue */}
        <button onClick={() => navigate("/summarizer")}>Continue</button>
      </div>
    );
  }

  if (error) {
    return (
      <div>
        <h2>Login Error</h2>
        <p>{error}</p>
        <button onClick={() => navigate("/login")}>Retry Login</button>
      </div>
    );
  }

  // Should not reach here, but for completeness:
  return <div>Signing you in…</div>;
}

export default OAuthCallback;
