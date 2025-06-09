import React from "react";

const ChatTab = ({ title, children }) => (
  <div className="flex flex-col h-full">
    <div className="text-lg font-semibold mb-4">{title}</div>
    <div className="flex-1 overflow-auto bg-white rounded shadow p-4">
      {children}
    </div>
  </div>
);

export default ChatTab; 