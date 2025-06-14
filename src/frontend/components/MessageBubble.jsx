import React from "react";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const MessageBubble = ({ message, sender, align = "left" }) => {
  const isUser = align === "right";
  
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-3xl px-4 py-3 rounded-lg shadow text-sm ${isUser ? "bg-blue-500 text-white" : "bg-gray-200 text-gray-900"}`}>
        <div className="font-semibold mb-2 text-xs opacity-70">{sender}</div>
        <div className="markdown-content leading-relaxed">
          <ReactMarkdown 
            remarkPlugins={[remarkGfm]}
            components={{
              // Inline code styling
              code({node, inline, className, children, ...props}) {
                if (inline) {
                  return (
                    <code 
                      className={`px-1 py-0.5 rounded text-xs font-mono ${
                        isUser ? "bg-blue-600 text-blue-100" : "bg-gray-800 text-green-400"
                      }`} 
                      {...props}
                    >
                      {children}
                    </code>
                  );
                }
                return (
                  <pre className={`p-3 rounded-md overflow-x-auto my-2 ${
                    isUser ? "bg-blue-600 text-blue-100" : "bg-gray-800 text-green-400"
                  }`}>
                    <code className="font-mono text-xs" {...props}>{children}</code>
                  </pre>
                );
              },
              // Block quote styling
              blockquote({children}) {
                return (
                  <blockquote className={`border-l-4 pl-4 italic my-2 ${
                    isUser ? "border-blue-300" : "border-blue-500"
                  }`}>
                    {children}
                  </blockquote>
                );
              },
              // List styling
              ul({children}) {
                return <ul className="list-disc list-inside my-2 space-y-1">{children}</ul>;
              },
              ol({children}) {
                return <ol className="list-decimal list-inside my-2 space-y-1">{children}</ol>;
              },
              // Link styling
              a({href, children}) {
                return (
                  <a 
                    href={href} 
                    className={`underline hover:no-underline ${
                      isUser ? "text-blue-200 hover:text-blue-100" : "text-blue-600 hover:text-blue-800"
                    }`} 
                    target="_blank" 
                    rel="noopener noreferrer"
                  >
                    {children}
                  </a>
                );
              },
              // Table styling
              table({children}) {
                return (
                  <table className={`border-collapse border my-2 w-full text-xs ${
                    isUser ? "border-blue-300" : "border-gray-400"
                  }`}>
                    {children}
                  </table>
                );
              },
              th({children}) {
                return (
                  <th className={`border px-2 py-1 font-semibold ${
                    isUser ? "border-blue-300 bg-blue-600" : "border-gray-400 bg-gray-300 text-gray-900"
                  }`}>
                    {children}
                  </th>
                );
              },
              td({children}) {
                return (
                  <td className={`border px-2 py-1 ${
                    isUser ? "border-blue-300" : "border-gray-400"
                  }`}>
                    {children}
                  </td>
                );
              },
              // Paragraph styling
              p({children}) {
                return <p className="my-1 leading-relaxed">{children}</p>;
              },
              // Heading styling
              h1({children}) {
                return <h1 className="text-lg font-bold my-2 leading-tight">{children}</h1>;
              },
              h2({children}) {
                return <h2 className="text-base font-bold my-2 leading-tight">{children}</h2>;
              },
              h3({children}) {
                return <h3 className="text-sm font-bold my-1 leading-tight">{children}</h3>;
              },
              // Strong/Bold styling
              strong({children}) {
                return <strong className="font-bold">{children}</strong>;
              },
              // Emphasis/Italic styling
              em({children}) {
                return <em className="italic">{children}</em>;
              }
            }}
                    >
            {message}
          </ReactMarkdown>
        </div>
      </div>
    </div>
  );
};

export default MessageBubble; 