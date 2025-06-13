const API_URL = import.meta.env.VITE_API_URL || '';

export async function sendMessage(message, chatName = null, modelId = null) {
  try {
    const body = { message };
    if (chatName) body.chat_name = chatName;
    if (modelId) body.model_id = modelId;
    const res = await fetch(`${API_URL}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body)
    });
    if (!res.ok) {
      const error = await res.json().catch(() => ({}));
      throw new Error(error.detail || 'Mesaj gönderilemedi');
    }
    return await res.json();
  } catch (err) {
    throw err;
  }
} 