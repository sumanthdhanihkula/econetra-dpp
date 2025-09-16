import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("Loading...");
  const [dpps, setDpps] = useState([]); // must be [] not null
  const apiUrl = "http://127.0.0.1:8000/dpp";

  // Fetch DPPs on load
  useEffect(() => {
    axios.get(apiUrl)
      .then((res) => {
        setDpps(res.data || []);  // fallback to [] if null
        setMessage("Backend Connected ✅");
      })
      .catch(() => setMessage("❌ Cannot connect to backend"));
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Econetra DPP Dashboard</h1>
      <p>{message}</p>

      <h2>All DPPs</h2>
      {Array.isArray(dpps) && dpps.length === 0 ? (
        <p>No records yet</p>
      ) : (
        <ul>
          {dpps.map((d) => (
            <li key={d.id}>
              <b>{d.name || d.product_name}</b> - {d.category} ({d.status || d.compliance_status})
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
