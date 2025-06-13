const API_URL = import.meta.env.VITE_API_URL || '';

export async function getFiles() {
  // TODO: Backend'de GET /files endpointi yoksa eklenmeli
  const res = await fetch(`${API_URL}/files`);
  if (!res.ok) throw new Error('Dosyalar alınamadı');
  return res.json();
}

export async function uploadFile(formData) {
  // TODO: Backend'de POST /files/upload endpointi yoksa eklenmeli
  const res = await fetch(`${API_URL}/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) throw new Error('Dosya yüklenemedi');
  return res.json();
}

export async function deleteFile(id) {
  // TODO: Backend'de DELETE /files/:id endpointi yoksa eklenmeli
  const res = await fetch(`${API_URL}/files/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Dosya silinemedi');
  return res.json();
}

export async function updateFile(id, fileData) {
  // TODO: Backend'de PUT /files/:id endpointi yoksa eklenmeli
  const res = await fetch(`${API_URL}/files/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(fileData)
  });
  if (!res.ok) throw new Error('Dosya güncellenemedi');
  return res.json();
} 