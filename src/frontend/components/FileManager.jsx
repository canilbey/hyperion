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
      {!loading && <div className="text-xs text-blue-grey-2 mt-2">Maksimum dosya boyutu: 100MB</div>}
    </div>
  );
}

const FileManager = () => {
  const [files, setFiles] = useState([]);
  const [openAccordionId, setOpenAccordionId] = useState(null);
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
    <div className="flex">
      {/* Sidebar */}
      <div className="w-80 p-4 border-r border-blue-grey-4">
        <FileDropzone onUpload={handleUpload} loading={loading} />
        {error && <div className="text-red-500 mb-2">{error}</div>}
        <ul className="space-y-3">
          {files.length === 0 && <li className="text-blue-grey-2">Hiç dosya yok</li>}
          {files.map((file) => (
            <li key={file.file_id || file.id} className="list-disc text-white">
              <span className="font-bold">{file.filename || file.name}</span>
            </li>
          ))}
        </ul>
      </div>
      {/* Main alan - Akordiyon */}
      <div className="flex-1 p-8">
        <div className="max-w-2xl mx-auto">
          <ul className="divide-y divide-blue-grey-4">
            {files.map((file) => (
              <li key={file.file_id || file.id}>
                <div className="flex items-center justify-between py-4 cursor-pointer hover:bg-blue-grey-4 rounded-xl px-4 transition"
                  onClick={() => setOpenAccordionId(openAccordionId === (file.file_id || file.id) ? null : (file.file_id || file.id))}>
                  <span className="font-bold text-white">{file.filename || file.name}</span>
                  <button
                    className="material-icons text-red-300 hover:text-red-500 text-2xl bg-transparent border-none p-0 ml-2"
                    onClick={e => { e.stopPropagation(); handleDelete(file.file_id || file.id); }}
                    aria-label="Sil"
                  >
                    delete
                  </button>
                </div>
                {openAccordionId === (file.file_id || file.id) && (
                  <div className="bg-blue-grey-5 rounded-xl p-6 mt-2 mb-4 text-white shadow">
                    <div className="mb-2 text-lg font-bold">Dosya Metadata</div>
                    <div className="space-y-1">
                      <div><b>ID:</b> {file.file_id}</div>
                      <div><b>Dosya Adı:</b> {file.filename}</div>
                      <div><b>İçerik Tipi:</b> {file.content_type}</div>
                      <div><b>Orijinal Boyut (byte):</b> {file.size}</div>
                      <div><b>Chunk Sayısı:</b> {file.num_chunks}</div>
                      <div><b>Chunk'lanmış Toplam Boyut (byte):</b> {file.chunked_total_size}</div>
                      <div><b>Yüklenme Tarihi:</b> {file.upload_time}</div>
                      <div><b>Kullanıcı ID:</b> {file.user_id || '-'}</div>
                    </div>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
};

export default FileManager; 