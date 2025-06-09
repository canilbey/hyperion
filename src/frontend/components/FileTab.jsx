import React from "react";

const FileTab = ({ file, onDelete }) => (
  <div className="bg-white rounded shadow p-4 flex flex-col gap-2">
    <div className="text-lg font-bold">{file.name}</div>
    <div className="text-xs text-gray-500">ID: {file.id}</div>
    <button className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600 mt-2 w-max" onClick={() => onDelete(file.id)}>Sil</button>
  </div>
);

export default FileTab; 