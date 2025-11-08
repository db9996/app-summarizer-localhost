import React, { useState, useEffect } from "react";
import Login from "./components/Login";
import Signup from "./components/Signup";
import Summarizer from "./components/Summarizer";
import History from "./components/History";
import OAuthCallback from "./components/OAuthCallback";
import { BrowserRouter, Routes, Route, useLocation, useNavigate } from "react-router-dom";
// IMPORTANT: Ensure index.css is imported in main.jsx, not here

function AppWrapper() {
  // Needed to use hooks inside Router context
  const location = useLocation();
  const navigate = useNavigate();

  const [token, setToken] = useState(localStorage.getItem("token"));
  const [view, setView] = useState(token ? "summarizer" : "login");

  // Sync view state with URL path on first load and whenever route changes
  useEffect(() => {
    if (!token) {
      // Not logged in
      if (location.pathname === "/signup") setView("signup");
      else if (location.pathname === "/login") setView("login");
      else if (location.pathname === "/oauth-callback") {
        // handled separately
      } else setView("login"); // Always show login/signup for "/"
    } else {
      // Logged in
      if (location.pathname === "/history") setView("history");
      else if (location.pathname === "/summarizer") setView("summarizer");
      else setView("summarizer");
    }
  }, [location.pathname, token]);

  useEffect(() => {
    const handleStorage = () => {
      setToken(localStorage.getItem("token"));
      setView(localStorage.getItem("token") ? "summarizer" : "login");
    };
    window.addEventListener("storage", handleStorage);
    return () => window.removeEventListener("storage", handleStorage);
  }, []);

  const handleLogin = (token) => {
    localStorage.setItem("token", token);
    setToken(token);
    setView("summarizer");
    navigate("/summarizer"); // You can change to /history if desired
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setToken(null);
    setView("login");
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex flex-col bg-gray-100">
      {/* Blue header */}
      <div className="blue-header"></div>
      {/* Nav - Switch nav button based on current route */}
      <nav className="nav">
        {token && (
          <>
            {location.pathname === "/summarizer" && (
              <button onClick={() => { setView("history"); navigate("/history"); }}>History</button>
            )}
            {location.pathname === "/history" && (
              <button onClick={() => { setView("summarizer"); navigate("/summarizer"); }}>Summarizer</button>
            )}
            {location.pathname !== "/login" && (
              <button onClick={handleLogout}>Logout</button>
            )}
          </>
        )}
      </nav>
      {/* Main content centered */}
      <div className="flex-1 flex items-center justify-center">
        <Routes>
          {/* OAuth callback: MANDATORY for Google/GitHub login */}
          <Route
            path="/oauth-callback"
            element={<OAuthCallback onLogin={handleLogin} />}
          />
          {!token && (
            <>
              <Route
                path="/login"
                element={
                  view === "login" && (
                    <Login
                      onLogin={handleLogin}
                      goToSignup={() => { setView("signup"); navigate("/signup"); }}
                    />
                  )
                }
              />
              <Route
                path="/signup"
                element={
                  view === "signup" && (
                    <Signup
                      onSignup={() => { setView("login"); navigate("/login"); }}
                      goToLogin={() => { setView("login"); navigate("/login"); }}
                    />
                  )
                }
              />
              <Route
                path="/"
                element={
                  view === "login" ? (
                    <Login
                      onLogin={handleLogin}
                      goToSignup={() => { setView("signup"); navigate("/signup"); }}
                    />
                  ) : (
                    <Signup
                      onSignup={() => { setView("login"); navigate("/login"); }}
                      goToLogin={() => { setView("login"); navigate("/login"); }}
                    />
                  )
                }
              />
              {/* ---- ONLY FIX: fallback to login on all other unknown routes ---- */}
              <Route
                path="*"
                element={
                  <Login
                    onLogin={handleLogin}
                    goToSignup={() => { setView("signup"); navigate("/signup"); }}
                  />
                }
              />
            </>
          )}
          {token && (
            <>
              <Route
                path="/summarizer"
                element={<Summarizer />}
              />
              <Route
                path="/history"
                element={<History />}
              />
              {/* NO "/" route for logged-in users */}
            </>
          )}
        </Routes>
      </div>
    </div>
  );
}

// Outer wrapper so we can use hooks in AppWrapper
function App() {
  return (
    <BrowserRouter>
      <AppWrapper />
    </BrowserRouter>
  );
}

export default App;
