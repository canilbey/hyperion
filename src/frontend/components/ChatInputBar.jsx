import React from "react";

const ChatInputBar = ({ value, onChange, onSend }) => (
  <form className="flex gap-2" onSubmit={e => { e.preventDefault(); onSend(); }}>
    <input
      className="flex-1 border rounded px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-400"
      type="text"
      placeholder="Mesajınızı yazın..."
      value={value}
      onChange={e => onChange(e.target.value)}
    />
    <button
      type="submit"
      className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition"
    >
      Gönder
    </button>
  </form>
);

export default ChatInputBar; 