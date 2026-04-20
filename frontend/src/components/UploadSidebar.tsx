import React, { useState, useRef, useCallback } from 'react';
import './UploadSidebar.css';

const INGESTION_URL = 'http://localhost:8001/upload';

interface HistoryEntry {
  filename: string;
  status: 'ok' | 'fail';
  chunks?: number;
  pages?: number;
}

interface UploadSidebarProps {
  onDocumentUploaded?: () => void;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const UploadSidebar: React.FC<UploadSidebarProps> = ({ onDocumentUploaded }) => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusMsg, setStatusMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [dragging, setDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFile = useCallback((f: File) => {
    if (!f.name.toLowerCase().endsWith('.pdf')) {
      setStatusMsg({ type: 'error', text: 'Only PDF files are supported.' });
      return;
    }
    setFile(f);
    setStatusMsg(null);
  }, []);

  const onDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files[0];
    if (dropped) handleFile(dropped);
  }, [handleFile]);

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setProgress(10);
    setStatusMsg(null);

    const formData = new FormData();
    formData.append('file', file);

    // Simulate progress ticks while waiting
    const ticker = setInterval(() => {
      setProgress(p => Math.min(p + 8, 85));
    }, 600);

    try {
      const res = await fetch(INGESTION_URL, { method: 'POST', body: formData });
      clearInterval(ticker);
      setProgress(100);

      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }
      const data = await res.json();

      if (data.status === 'success' || data.status === 'partial_failure') {
        const msg = `✓ Processed ${data.pages_processed ?? '?'} pages, ${data.total_chunks ?? '?'} chunks, ${data.images_saved ?? 0} images.`;
        setStatusMsg({ type: 'success', text: msg });
        setHistory(h => [{ filename: file.name, status: 'ok', chunks: data.total_chunks, pages: data.pages_processed }, ...h].slice(0, 10));
        onDocumentUploaded?.();
      } else {
        throw new Error(data.error ?? 'Unknown error from server.');
      }
    } catch (err: unknown) {
      clearInterval(ticker);
      const message = err instanceof Error ? err.message : 'Upload failed';
      setStatusMsg({ type: 'error', text: message });
      if (file) setHistory(h => [{ filename: file.name, status: 'fail' }, ...h].slice(0, 10));
    } finally {
      setUploading(false);
      setProgress(0);
      setFile(null);
    }
  };

  return (
    <>
      <p className="section-label">Document Ingestion</p>

      <div className="upload-card">
        {/* Dropzone */}
        <div
          className={`dropzone ${dragging ? 'dragging' : ''}`}
          onClick={() => fileInputRef.current?.click()}
          onDragOver={e => { e.preventDefault(); setDragging(true); }}
          onDragLeave={() => setDragging(false)}
          onDrop={onDrop}
          role="button"
          tabIndex={0}
          onKeyDown={e => e.key === 'Enter' && fileInputRef.current?.click()}
          aria-label="Click or drag to upload PDF"
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf"
            onChange={e => e.target.files?.[0] && handleFile(e.target.files[0])}
            id="pdf-file-input"
          />
          <div className="dropzone-icon">📄</div>
          <p className="dropzone-title">Upload PDF</p>
          <p className="dropzone-sub">
            {dragging ? 'Drop it here!' : 'Click or drag & drop your document'}
          </p>
        </div>

        {/* File preview */}
        {file && (
          <div className="file-preview">
            <span className="file-icon">📑</span>
            <div className="file-info">
              <p className="file-name">{file.name}</p>
              <p className="file-size">{formatBytes(file.size)}</p>
            </div>
            <button className="file-remove-btn" onClick={() => setFile(null)} title="Remove">✕</button>
          </div>
        )}

        {/* Progress */}
        {uploading && (
          <div className="progress-wrap">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${progress}%` }} />
            </div>
            <p className="progress-label">Processing document… {progress}%</p>
          </div>
        )}

        {/* Status */}
        {statusMsg && (
          <div className={`status-banner ${statusMsg.type}`}>
            <span className="banner-icon">{statusMsg.type === 'success' ? '✅' : '⚠️'}</span>
            <span className="banner-text">{statusMsg.text}</span>
          </div>
        )}

        {/* Upload Button */}
        <div className="upload-btn-wrap">
          <button
            id="upload-btn"
            className="btn-primary"
            onClick={handleUpload}
            disabled={!file || uploading}
          >
            {uploading ? '⏳ Uploading…' : '🚀 Ingest Document'}
          </button>
        </div>
      </div>

      {/* History */}
      {history.length > 0 && (
        <div>
          <p className="section-label" style={{ marginBottom: '10px' }}>Recent Uploads</p>
          <div className="upload-history">
            {history.map((h, i) => (
              <div className="history-item" key={i}>
                <span>📄</span>
                <span className="history-filename">{h.filename}</span>
                <span className={`history-badge ${h.status === 'ok' ? 'ok' : 'fail'}`}>
                  {h.status === 'ok' ? `${h.pages}p / ${h.chunks}c` : 'Failed'}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
};

export default UploadSidebar;
