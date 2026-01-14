import { useState } from "react";
import { api } from "../api/client";

export default function UploadDocument() {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] =
    useState<"idle" | "uploading" | "success" | "error">("idle");

  const upload = async () => {
    if (!file) return;

    setStatus("uploading");

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/documents/upload", formData);
      setStatus("success");
      setFile(null);
    } catch {
      setStatus("error");
    }
  };

  return (
    <div className="card upload-card">

      <h3 className="card-title">Upload Knowledge Base</h3>
      <p className="card-subtitle">
        Add company documents to your private AI knowledge base
      </p>

      <label className="file-picker">
        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
        />
        <span>{file ? file.name : "Select PDF Document"}</span>
      </label>

      <button
        className="primary full-width"
        onClick={upload}
        disabled={status === "uploading"}
      >
        {status === "uploading" ? "Uploading..." : "Upload Document"}
      </button>

      {status === "success" && (
        <p className="status success">
          ✅ Document uploaded & processing started
        </p>
      )}

      {status === "error" && (
        <p className="status error">
          ❌ Upload failed. Please login again.
        </p>
      )}
    </div>
  );
}
