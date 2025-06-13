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

const ChatContainer = () => {
  const [chats, setChats] = useState([]); // Sohbet başlıkları
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [messages, setMessages] = useState([]); // {role, content}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [editingTitleId, setEditingTitleId] = useState(null);
  const [titleInput, setTitleInput] = useState("");

  // Chat listesi ve modelleri yükle
  useEffect(() => {
    getChats().then(setChats).catch(() => setChats([]));
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
        .then(msgs => setMessages(msgs.map(m => ({ sender: m.role === "user" ? "Kullanıcı" : "Asistan", message: m.content }))))
        .catch(() => setMessages([]))
        .finally(() => setLoading(false));
    } else {
      setMessages([]);
    }
  }, [selectedChatId]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "Kullanıcı", message: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const res = await sendMessage({ message: input, model_id: selectedModel, chat_id: selectedChatId });
      setMessages((msgs) => [
        ...msgs,
        { sender: "Asistan", message: res.message?.content || "(Yanıt yok)" }
      ]);
      // Eğer yeni chat başlatıldıysa chat_id dönebilir, chat listesini güncelle
      if (res.chat_id && !selectedChatId) {
        setSelectedChatId(res.chat_id);
        getChats().then(setChats);
      }
    } catch (err) {
      setError(err.message || "Bir hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  const handleSelectChat = (chatId) => {
    setSelectedChatId(chatId);
    setError(null);
  };

  const handleDeleteChat = async (chatId) => {
    if (!window.confirm("Sohbet silinsin mi?")) return;
    try {
      await deleteChat(chatId);
      setChats(chats.filter(c => c.chat_id !== chatId));
      if (selectedChatId === chatId) {
        setSelectedChatId(null);
        setMessages([]);
      }
    } catch (err) {
      setError(err.message || "Sohbet silinemedi");
    }
  };

  const handleNewChat = () => {
    setSelectedChatId(null);
    setMessages([]);
    setError(null);
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

  const chatsSafe = Array.isArray(chats) ? chats : [];
  const modelsSafe = Array.isArray(models) ? models : [];

  return (
    <div className="flex h-full">
      {/* Sidebar: Sohbet listesi */}
      <div className="w-80 p-4 border-r border-blue-grey-4">
        <div className="mb-2 font-bold text-md flex items-center justify-between">
          <span>Sohbetler</span>
          <button
            className="w-8 h-8 flex items-center justify-center rounded bg-blue-grey-5 text-white hover:bg-blue-grey-4 transition text-xl p-0"
            onClick={handleNewChat}
            aria-label="Yeni Chat"
          >
            <span className="material-icons text-lg">add</span>
          </button>
        </div>
        <ul className="space-y-3">
          {chatsSafe.length === 0 && <li className="text-blue-grey-2">Hiç sohbet yok</li>}
          {chatsSafe.map(chat => (
            <li key={chat.chat_id} className="list-disc text-white flex items-center justify-between">
              {editingTitleId === chat.chat_id ? (
                <>
                  <input
                    className="flex-1 px-2 py-1 rounded bg-blue-grey-4 text-white mr-2"
                    value={titleInput}
                    onChange={e => setTitleInput(e.target.value)}
                    onBlur={() => setEditingTitleId(null)}
                    onKeyDown={e => { if (e.key === 'Enter') handleSaveTitle(chat.chat_id); }}
                    autoFocus
                  />
                  <button className="material-icons text-green-400 hover:text-green-600 text-xl p-0 mr-1" onClick={() => handleSaveTitle(chat.chat_id)}>check</button>
                  <button className="material-icons text-red-400 hover:text-red-600 text-xl p-0" onClick={() => setEditingTitleId(null)}>close</button>
                </>
              ) : (
                <>
                  <button
                    className={`w-full text-left px-4 py-2 font-medium transition border-none outline-none bg-transparent ${selectedChatId === chat.chat_id ? 'bg-blue-grey-4 text-white' : 'bg-blue-grey-5 text-white hover:bg-blue-grey-4'}`}
                    onClick={() => handleSelectChat(chat.chat_id)}
                  >
                    {chat.label || chat.chat_id}
                  </button>
                  <button
                    className="material-icons text-blue-300 hover:text-blue-500 text-xl bg-transparent border-none p-0 ml-1"
                    onClick={() => handleEditTitle(chat)}
                    aria-label="Başlığı Düzenle"
                  >
                    edit
                  </button>
                  <button
                    className="material-icons text-red-300 hover:text-red-500 text-2xl bg-transparent border-none p-0 ml-1"
                    onClick={() => handleDeleteChat(chat.chat_id)}
                    aria-label="Sil"
                  >
                    delete
                  </button>
                </>
              )}
            </li>
          ))}
        </ul>
      </div>
      {/* Main alan: Model seçimi, geçmiş ve input */}
      <div className="flex-1 flex flex-col h-full p-8">
        <div className="flex items-center gap-4 mb-4">
          <label className="text-sm font-medium">Model Seç:</label>
          <select
            className="bg-blue-grey-4 text-white rounded px-3 py-2"
            value={selectedModel}
            onChange={e => setSelectedModel(e.target.value)}
          >
            {modelsSafe.map(m => (
              <option key={m.id || m.model_id} value={m.id || m.model_id}>{m.name || m.model_name}</option>
            ))}
          </select>
        </div>
        {selectedChatId ? (
          <ChatArea
            inputBar={
              <ChatInputBar
                value={input}
                onChange={setInput}
                onSend={handleSend}
              />
            }
          >
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
          </ChatArea>
        ) : (
          <div className="flex-1 flex flex-col items-center justify-center text-blue-grey-2 text-lg opacity-70">
            Sohbet seçin veya yeni bir sohbet başlatın.
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatContainer; 