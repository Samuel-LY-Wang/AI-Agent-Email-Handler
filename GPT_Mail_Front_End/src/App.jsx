import React, { useState, useEffect } from "react";

function App() {
  const [userEmail, setUserEmail] = useState(null);
  const [warning, setWarning] = useState(null);
  const [errorKey, setErrorKey] = useState(null);
  const [result, setResult] = useState(null);

  useEffect(() => {
    // Parse email and warning from URL query params after redirect from OAuth
    const params = new URLSearchParams(window.location.search);
    const email = params.get("email");
    const warn = params.get("warning");
    const err = params.get("error");
    if (email) {
      setUserEmail(email);
      // remove query params from URL without reloading
      const newUrl = window.location.pathname;
      window.history.replaceState({}, document.title, newUrl);
    }
    if (warn) setWarning(warn);
    if (err) setErrorKey(err);
  }, []);

  const friendlyError = (key) => {
    switch (key) {
      case "auth_invalid_grant":
        return "Authentication failed (invalid grant). Please try signing in again.";
      case "auth_denied":
        return "You denied access. Please allow access to continue.";
      case "auth_failed":
        return "Authentication failed. Please try again.";
      case "user_not_authenticated":
        return "You are not authenticated. Please sign in.";
      case "invalid_user_email":
        return "The email provided is not valid for the authenticated account. Check that you used the same account you signed in with.";
      case "permission_denied":
        return "Permission denied when accessing Gmail. Ensure the app has the required scopes and try re-authenticating.";
      case "agent_failed":
        return "The agent encountered an unexpected error while running. Check the server logs.";
      case "missing_fields":
        return "The request is missing required fields for this user. Provide mode, blacklist, whitelist, and relation.";
      default:
        return null;
    }
  };

  const handleGoogleSignIn = () => {
    window.location.href = "http://127.0.0.1:8000/auth/google";
  };

  // Example: after auth, user manually enters their email (or it's auto-filled)
  const handleRunAgent = async () => {
    const data = {
      [userEmail]: {
        mode: "blacklist",
        blacklist: [],
        whitelist: [],
        relation: {}
      }
    };
    const res = await fetch("http://127.0.0.1:8000/run-agent", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });
    const json = await res.json();
    setResult(json);
  };

  return (
    <div>
      <h1>Email Agent Frontend</h1>
      <button onClick={handleGoogleSignIn}>Sign in with Google</button>
      <input
        type="email"
        placeholder="Enter your email after login"
        value={userEmail || ""}
        onChange={e => setUserEmail(e.target.value)}
      />
      {warning && (
        <div style={{ color: "orange", marginTop: 8 }}>
          Warning: {warning === "no_refresh_token" ? "No refresh token received — you may need to re-authenticate later." : warning}
        </div>
      )}
      <button onClick={handleRunAgent}>Run Agent</button>
      {errorKey && (
        <div style={{ color: "red", marginTop: 8 }}>
          {friendlyError(errorKey) || "Authentication error"}
        </div>
      )}

      {result && (
        <div style={{ marginTop: 12 }}>
          {result.status === "ok" ? (
            <div>
              <strong>Agent run results</strong>
              <ul>
                {result.results.map(r => (
                  <li key={r.user} style={{ marginTop: 6 }}>
                    {r.user}: {r.status === "success" ? (
                      <span>drafted {r.drafted} emails</span>
                    ) : (
                      <span style={{ color: 'red' }}>{friendlyError(r.error) || r.error}: {r.message}</span>
                    )}
                  </li>
                ))}
              </ul>
            </div>
          ) : (
            <pre>{JSON.stringify(result, null, 2)}</pre>
          )}
        </div>
      )}
    </div>
  );
}

export default App;