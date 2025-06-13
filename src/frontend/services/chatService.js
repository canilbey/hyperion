const API_URL = import.meta.env.VITE_API_URL || '';

export async function sendMessage({ message, model_id, chat_id }) {
  const url = chat_id ? `${API_URL}/chat/${chat_id}` : `${API_URL}/chat`;
  const body = chat_id
    ? { messages: [{ role: 'user', content: message }], custom_config: model_id ? { model_id } : undefined }
    : { messages: [{ role: 'user', content: message }], custom_config: model_id ? { model_id } : undefined };
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) throw new Error('Mesaj gönderilemedi');
  return res.json();
}

export async function getChats() {
  const res = await fetch(`${API_URL}/chats`);
  if (!res.ok) throw new Error('Sohbetler alınamadı');
  return res.json();
}

export async function getChatHistory(chat_id) {
  const res = await fetch(`${API_URL}/chats/${chat_id}/messages`);
  if (!res.ok) throw new Error('Sohbet geçmişi alınamadı');
  return res.json();
}

export async function deleteChat(chat_id) {
  const res = await fetch(`${API_URL}/chats/${chat_id}`, { method: 'DELETE' });
  if (!res.ok) throw new Error('Sohbet silinemedi');
  return res.json();
} 