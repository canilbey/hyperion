const API_URL = import.meta.env.VITE_API_URL || '';

export async function getModels() {
  const res = await fetch(`${API_URL}/models`);
  if (!res.ok) throw new Error('Modeller alınamadı');
  return res.json();
}

export async function addModel(modelData) {
  const res = await fetch(`${API_URL}/model/create`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(modelData)
  });
  if (!res.ok) throw new Error('Model eklenemedi');
  return res.json();
}

export async function deleteModel(id) {
  // TODO: Backend'de DELETE /model/:id endpointi yoksa eklenmeli
  const res = await fetch(`${API_URL}/model/${id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Model silinemedi');
  return res.json();
}

export async function updateModel(id, modelData) {
  // TODO: Backend'de PATCH /model/:id endpointi yoksa eklenmeli
  const res = await fetch(`${API_URL}/model/${id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(modelData)
  });
  if (!res.ok) throw new Error('Model güncellenemedi');
  return res.json();
} 