import React, { useState, useEffect } from "react";
import ChatArea from "./ChatArea";
import ChatInputBar from "./ChatInputBar";
import MessageBubble from "./MessageBubble";
import { sendMessage } from "../services/chatService";
import { getModels } from "../services/modelService";

const ChatContainer = () => {
  const [messages, setMessages] = useState([]); // {sender, message}
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");

  useEffect(() => {
    getModels().then(data => {
      setModels(data);
      if (data.length > 0) setSelectedModel(data[0].id);
    });
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { sender: "Kullanıcı", message: input };
    setMessages((msgs) => [...msgs, userMsg]);
    setInput("");
    setLoading(true);
    setError(null);
    try {
      const res = await sendMessage(input, undefined, selectedModel);
      setMessages((msgs) => [
        ...msgs,
        { sender: "Asistan", message: res.message?.content || "(Yanıt yok)" }
      ]);
    } catch (err) {
      setError(err.message || "Bir hata oluştu");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-4 mb-2">
        <label className="text-sm font-medium">Model Seç:</label>
        <select
          className="bg-blue-grey-4 text-white rounded px-3 py-2"
          value={selectedModel}
          onChange={e => setSelectedModel(e.target.value)}
        >
          {models.map(m => (
            <option key={m.id} value={m.id}>{m.name}</option>
          ))}
        </select>
      </div>
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
    </div>
  );
};

export default ChatContainer; 