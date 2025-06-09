import React from "react";

const ChatArea = ({ children, inputBar }) => (
  <div className="flex flex-col h-full">
    <div className="flex-1 overflow-y-auto space-y-2 pb-4">{children}</div>
    <div className="pt-2 border-t mt-2">{inputBar}</div>
  </div>
);

export default ChatArea; 