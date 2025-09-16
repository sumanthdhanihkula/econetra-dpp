import React, { useState } from "react";

function InvoiceUpload({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [msg, setMsg] = useState("");

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setMsg("");
  };

  const handleUpload = async () => {
    if (!file) return setMsg("No file selected.");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://127.0.0.1:8000/extract-invoice", {
        method: "POST",
        body: formData,
      });
      if (!response.ok) throw new Error("Upload failed");
      setMsg("Upload successful!");
      if (onUploaded) onUploaded();
    } catch {
      setMsg("Error during upload.");
    }
  };

  return (
    <div style={{ marginBottom: 24 }}>
      <input type="file" onChange={handleFileChange} accept=".pdf, image/*" />
      <button onClick={handleUpload} style={{ marginLeft: 8 }}>
        Upload Invoice
      </button>
      {msg && <div>{msg}</div>}
    </div>
  );
}

export default InvoiceUpload;
