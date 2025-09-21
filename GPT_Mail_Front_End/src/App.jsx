import React, { useState } from "react";

function App() {
  const [userEmail, setUserEmail] = useState(null);
  const [result, setResult] = useState(null);

  const handleGoogleSignIn = () => {
    window.location.href = "http://127.0.0.1:8000/auth/google";
  };

  // Example: after auth, user manually enters their email
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
    setResult(await res.json());
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
      <button onClick={handleRunAgent}>Run Agent</button>
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  );
}

export default App;