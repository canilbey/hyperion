import React, { useState, useRef, useEffect } from "react";
import { getFiles, uploadFile, deleteFile, updateFile } from "../services/fileService";

function ActionMenu({ open, onDelete, onEdit, onClose }) {
  const menuRef = useRef();
  React.useEffect(() => {
    if (!open) return;
    const handleMouseLeave = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.relatedTarget)) {
        onClose();
      }
    };
    const node = menuRef.current;
    if (node) node.addEventListener('mouseleave', handleMouseLeave);
    return () => node && node.removeEventListener('mouseleave', handleMouseLeave);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div ref={menuRef} className="absolute right-0 mt-2 w-36 bg-blue-grey-5 text-white border border-blue-grey-4 z-50 flex flex-col py-1">
      <button className="w-full text-left px-5 py-2 transition font-medium bg-blue-grey-5 text-white hover:bg-blue-grey-4 rounded-none" onClick={onEdit}>Düzenle</button>
      <button className="w-full text-left px-5 py-2 transition font-medium bg-blue-grey-5 text-white hover:bg-red-400 rounded-none" onClick={onDelete}>Sil</button>
    </div>
  );
}

function FileDropzone({ onUpload, loading }) {
  const inputRef = useRef();
  const [dragActive, setDragActive] = useState(false);
  const handleDrop = e => {
    e.preventDefault();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      onUpload(e.dataTransfer.files[0]);
    }
  };
  const handleChange = e => {
    if (e.target.files && e.target.files[0]) {
      onUpload(e.target.files[0]);
    }
  };
  return (
    <div
      className={`border-2 border-dashed rounded-xl p-6 mb-4 text-center transition ${dragActive ? "border-blue-400 bg-blue-grey-4" : "border-blue-grey-3 bg-blue-grey-5"}`}
      onDragOver={e => { e.preventDefault(); setDragActive(true); }}
      onDragLeave={e => { e.preventDefault(); setDragActive(false); }}
      onDrop={handleDrop}
      onClick={() => inputRef.current && inputRef.current.click()}
      style={{ cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.6 : 1 }}
    >
      <input
        ref={inputRef}
        type="file"
        className="hidden"
        onChange={handleChange}
        disabled={loading}
      />
      {loading ? "Yükleniyor..." : "Dosya eklemek için tıkla veya sürükle-bırak yap"}
    </div>
  );
}

const FileManager = () => {
  const [files, setFiles] = useState([]);
  const [selectedId, setSelectedId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchFiles();
  }, []);

  const fetchFiles = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getFiles();
      setFiles(data);
    } catch (err) {
      setError(err.message || "Dosyalar alınamadı");
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async (file) => {
    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append("file", file);
    try {
      await uploadFile(formData);
      fetchFiles();
    } catch (err) {
      setError(err.message || "Dosya yüklenemedi");
    } finally {
      setLoading(false);
    }
  };

  const handleEdit = async (file) => {
    const name = prompt("Yeni dosya adı:", file.name);
    if (!name) return;
    try {
      await updateFile(file.id, { ...file, name });
      fetchFiles();
    } catch (err) {
      setError(err.message || "Dosya güncellenemedi");
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("Dosya silinsin mi?")) return;
    try {
      await deleteFile(id);
      fetchFiles();
    } catch (err) {
      setError(err.message || "Dosya silinemedi");
    }
  };

  return (
    <div>
      <FileDropzone onUpload={handleUpload} loading={loading} />
      {error && <div className="text-red-500 mb-2">{error}</div>}
      <ul className="space-y-3 pl-4">
        {files.map((file) => (
          <li key={file.id} className="list-disc text-white relative">
            <button
              className={`w-full text-left px-4 py-2 font-medium transition border-none outline-none flex items-center justify-between bg-transparent
                ${selectedId === file.id ? 'bg-blue-grey-4 text-white' : 'bg-blue-grey-5 text-white hover:bg-blue-grey-4'}
              `}
              onClick={() => setSelectedId(file.id)}
            >
              <span>{file.name}</span>
              <span className="relative">
                <button
                  className="w-10 h-10 flex items-center justify-center rounded bg-blue-grey-5 text-white hover:bg-blue-grey-3 transition text-2xl ml-2 p-0"
                  onClick={e => { e.stopPropagation(); }}
                  aria-label="Aksiyonlar"
                >
                  &#8942;
                </button>
                <ActionMenu
                  open={selectedId === file.id}
                  onEdit={() => handleEdit(file)}
                  onDelete={() => handleDelete(file.id)}
                  onClose={() => setSelectedId(null)}
                />
              </span>
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default FileManager; 