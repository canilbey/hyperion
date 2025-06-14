import React, { useState, useEffect } from "react";
import ChatArea from "./ChatArea";
import ChatInputBar from "./ChatInputBar";
import MessageBubble from "./MessageBubble";
import { sendMessage, getChats, getChatHistory, deleteChat } from "../services/chatService";
import { getModels } from "../services/modelService";

// PATCH endpointi için ek fonksiyon
async function updateChatTitle(chat_id, newTitle) {
  const API_URL = import.meta.env.VITE_API_URL || '';
  const res = await fetch(`${API_URL}/chats/${chat_id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ label: newTitle })
  });
  if (!res.ok) throw new Error('Başlık güncellenemedi');
  return res.json();
}

const ChatContainer = ({ selectedChatId, setSelectedChatId, chats, setChats }) => {
  const [messages, setMessages] = useState([]); // {role, content}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [editingTitleId, setEditingTitleId] = useState(null);
  const [titleInput, setTitleInput] = useState("");
  const [newChatStarted, setNewChatStarted] = useState(false);

  useEffect(() => {
    getModels().then(data => {
      setModels(data);
      if (data.length > 0) setSelectedModel(data[0].id || data[0].model_id);
    });
  }, []);

  // Chat geçmişi yükle
  useEffect(() => {
    if (selectedChatId) {
      setLoading(true);
      getChatHistory(selectedChatId)
        .then(msgs => {
          // Eğer sadece ilk mesaj ve yanıtı varsa, history'yi eklemeye gerek yok
          // Eğer başka mesaj yoksa, history'yi yükle
          setMessages(msgs.map(m => ({ sender: m.role === "user" ? "Kullanıcı" : "Asistan", message: m.content })));
        })
        .catch(() => setMessages([]))
        .finally(() => setLoading(false));
    } else {
      setMessages([]);
      setNewChatStarted(false);
    }
  }, [selectedChatId]);

  const handleSend = async () => {
    if (!input.trim()) return;
    setLoading(true);
    setError(null);
    try {
      let userMsg = { sender: "Kullanıcı", message: input };
      let newMessages = [...messages, userMsg];
      setMessages(newMessages);
      const currentInput = input;
      setInput("");
      
      if (!selectedChatId) {
        // Yeni chat başladığını işaretle
        setNewChatStarted(true);
        
        // Backend'e mesaj gönder ve yeni chat oluştur
        const res = await sendMessage({ message: currentInput, model_id: selectedModel });
        
        // Chat ID'yi ayarla ve chat listesini güncelle
        setSelectedChatId(res.chat_id);
        setNewChatStarted(false);
        getChats().then(setChats);
        
        setMessages((msgs) => [
          ...msgs,
          { sender: "Asistan", message: res.message?.content || "(Yanıt yok)" }
        ]);
      } else {
        // Seçili chat varsa normal şekilde devam et
        const res = await sendMessage({ message: currentInput, model_id: selectedModel, chat_id: selectedChatId });
        setMessages((msgs) => [
          ...msgs,
          { sender: "Asistan", message: res.message?.content || "(Yanıt yok)" }
        ]);
      }
    } catch (err) {
      setError(err.message || "Bir hata oluştu");
    } finally {
      setLoading(false);
    }
  };



  const handleEditTitle = (chat) => {
    setEditingTitleId(chat.chat_id);
    setTitleInput(chat.label || "");
  };

  const handleSaveTitle = async (chat_id) => {
    if (!titleInput.trim()) return;
    try {
      await updateChatTitle(chat_id, titleInput);
      setChats(chats.map(c => c.chat_id === chat_id ? { ...c, label: titleInput } : c));
      setEditingTitleId(null);
    } catch (err) {
      setError(err.message || "Başlık güncellenemedi");
    }
  };

  return (
    <div className="flex flex-col h-full p-8">
      <div className="flex items-center gap-4 mb-4">
        <label className="text-sm font-medium">Model Seç:</label>
        <select
          className="bg-blue-grey-4 text-white rounded px-3 py-2"
          value={selectedModel}
          onChange={e => setSelectedModel(e.target.value)}
        >
          {models.map(m => (
            <option key={m.id || m.model_id} value={m.id || m.model_id}>{m.name || m.model_name}</option>
          ))}
        </select>
      </div>
      <div className="flex flex-col flex-1 min-h-0">
        {selectedChatId || newChatStarted ? (
          <div className="flex flex-col flex-1 min-h-0">
            <div className="flex-1 overflow-y-auto space-y-2 pb-4" style={{scrollbarGutter:'stable'}}>
              {messages.map((msg, i) => (
                <MessageBubble
                  key={i}
                  message={msg.message}
                  sender={msg.sender}
                  align={msg.sender === "Kullanıcı" ? "right" : "left"}
                />
              ))}
              {loading && <div className="text-xs text-gray-500">Yanıt bekleniyor...</div>}
              {error && <div className="text-xs text-red-500">{error}</div>}
            </div>
            <div className="pt-2 border-t mt-2 sticky bottom-0 bg-blue-grey-5 z-10">
              <ChatInputBar
                value={input}
                onChange={setInput}
                onSend={handleSend}
              />
            </div>
          </div>
        ) : (
          <div className="flex flex-col flex-1 min-h-0 items-center justify-center text-blue-grey-2 text-lg opacity-70">
            Sohbet seçin veya yeni bir sohbet başlatın.
            <div className="w-full max-w-2xl mt-8">
              <ChatInputBar
                value={input}
                onChange={setInput}
                onSend={handleSend}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatContainer; 