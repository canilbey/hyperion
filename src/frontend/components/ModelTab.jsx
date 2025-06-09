import React from "react";

const ModelTab = ({ model, onEdit, onDelete }) => (
  <div className="bg-white rounded shadow p-4 flex flex-col gap-2">
    <div className="text-lg font-bold">{model.name}</div>
    <div className="text-xs text-gray-500">ID: {model.id}</div>
    <div className="flex gap-2 mt-2">
      <button className="bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600" onClick={() => onEdit(model)}>Düzenle</button>
      <button className="bg-red-500 text-white px-3 py-1 rounded hover:bg-red-600" onClick={() => onDelete(model.id)}>Sil</button>
    </div>
  </div>
);

export default ModelTab; 