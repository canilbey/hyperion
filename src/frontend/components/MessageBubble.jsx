import React from "react";

const MessageBubble = ({ message, sender, align = "left" }) => (
  <div className={`flex ${align === "right" ? "justify-end" : "justify-start"}`}>
    <div className={`max-w-md px-4 py-2 rounded-lg shadow text-sm ${align === "right" ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-900"}`}>
      <div className="font-semibold mb-1 text-xs opacity-70">{sender}</div>
      <div>{message}</div>
    </div>
  </div>
);

export default MessageBubble; 