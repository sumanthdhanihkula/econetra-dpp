import React, { useState, useEffect } from "react";
import axios from "axios";

function App() {
  const [message, setMessage] = useState("Loading...");
  const [dpps, setDpps] = useState([]);
  const [form, setForm] = useState({ name: "", category: "", status: "" });
  const [editId, setEditId] = useState(null);

  const apiUrl = "http://127.0.0.1:8000/dpp";

  // Fetch all DPPs
  const fetchDpps = async () => {
    try {
      const res = await axios.get(apiUrl);
      setDpps(res.data || []);
      setMessage("Backend Connected ✅");
    } catch {
      setMessage("❌ Cannot connect to backend");
    }
  };

  // Add or Update DPP
  const saveDpp = async (e) => {
    e.preventDefault();
    try {
      if (editId) {
        await axios.put(`${apiUrl}/${editId}`, form);
        setEditId(null);
      } else {
        await axios.post(apiUrl, form);
      }
      setForm({ name: "", category: "", status: "" });
      fetchDpps();
    } catch {
      setMessage("❌ Failed to save DPP");
    }
  };

  // Delete a DPP
  const deleteDpp = async (id) => {
    try {
      await axios.delete(`${apiUrl}/${id}`);
      fetchDpps();
    } catch {
      alert("❌ Failed to delete DPP");
    }
  };

  // Edit a DPP
  const editDpp = (d) => {
    setEditId(d.id);
    setForm({ name: d.name, category: d.category, status: d.status });
  };

  useEffect(() => {
    fetchDpps();
  }, []);

  return (
    <div style={{ padding: "20px", fontFamily: "Arial" }}>
      <h1>Econetra DPP Dashboard</h1>
      <p>{message}</p>

      <h2>{editId ? "Edit DPP" : "Add New DPP"}</h2>
      <form onSubmit={saveDpp} style={{ marginBottom: "20px" }}>
        <input
          placeholder="Name"
          value={form.name}
          onChange={(e) => setForm({ ...form, name: e.target.value })}
          required
        />
        <input
          placeholder="Category"
          value={form.category}
          onChange={(e) => setForm({ ...form, category: e.target.value })}
          required
        />
        <input
          placeholder="Status"
          value={form.status}
          onChange={(e) => setForm({ ...form, status: e.target.value })}
          required
        />
        <button type="submit">{editId ? "Update DPP" : "Add DPP"}</button>
        {editId && (
          <button
            type="button"
            onClick={() => {
              setEditId(null);
              setForm({ name: "", category: "", status: "" });
            }}
            style={{ marginLeft: "10px" }}
          >
            Cancel
          </button>
        )}
      </form>

      <h2>All DPPs</h2>
      {dpps.length === 0 ? (
        <p>No records yet</p>
      ) : (
        <ul>
          {dpps.map((d) => (
            <li key={d.id}>
              <b>{d.name}</b> – {d.category} ({d.status})
              <button
                style={{ marginLeft: "10px" }}
                onClick={() => editDpp(d)}
              >
                Edit
              </button>
              <button
                style={{ marginLeft: "10px", color: "red" }}
                onClick={() => deleteDpp(d.id)}
              >
                Delete
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export default App;
