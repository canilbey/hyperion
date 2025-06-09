import React, { useState, useRef } from "react";

function ActionMenu({ open, onEdit, onDelete, onClose }) {
  const menuRef = useRef();
  React.useEffect(() => {
    if (!open) return;
    const handleMouseLeave = (e) => {
      if (menuRef.current && !menuRef.current.contains(e.relatedTarget)) {
        onClose();
      }
    };
    const node = menuRef.current;
    if (node) node.addEventListener('mouseleave', handleMouseLeave);
    return () => node && node.removeEventListener('mouseleave', handleMouseLeave);
  }, [open, onClose]);
  if (!open) return null;
  return (
    <div ref={menuRef} className="absolute right-0 mt-2 w-36 bg-blue-grey-5 text-white border border-blue-grey-4 z-50 flex flex-col py-1">
      <button className="w-full text-left px-5 py-2 transition font-medium bg-blue-grey-5 text-white hover:bg-blue-grey-4 rounded-none" onClick={onEdit}>Düzenle</button>
      <button className="w-full text-left px-5 py-2 transition font-medium bg-blue-grey-5 text-white hover:bg-red-400 rounded-none" onClick={onDelete}>Sil</button>
    </div>
  );
}

const ModelManager = ({ models, onAdd, onEdit, onDelete, selectedId, onSelect }) => {
  const [menuOpen, setMenuOpen] = useState(null);
  return (
    <ul className="space-y-3 pl-4">
      {models.map((model) => (
        <li key={model.id} className="list-disc text-white relative">
          <button
            className={`w-full text-left px-4 py-2 font-medium transition border-none outline-none flex items-center justify-between bg-transparent
              ${selectedId === model.id ? 'bg-blue-grey-4 text-white' : 'bg-blue-grey-5 text-white hover:bg-blue-grey-4'}
            `}
            onClick={() => onSelect && onSelect(model.id)}
          >
            <span>{model.name}</span>
            <span className="relative">
              <button
                className="w-10 h-10 flex items-center justify-center rounded bg-blue-grey-5 text-white hover:bg-blue-grey-3 transition text-2xl ml-2 p-0"
                onClick={e => { e.stopPropagation(); setMenuOpen(menuOpen === model.id ? null : model.id); }}
                aria-label="Aksiyonlar"
              >
                &#8942;
              </button>
              <ActionMenu
                open={menuOpen === model.id}
                onEdit={() => { setMenuOpen(null); onEdit(model); }}
                onDelete={() => { setMenuOpen(null); onDelete(model.id); }}
                onClose={() => setMenuOpen(null)}
              />
            </span>
          </button>
        </li>
      ))}
    </ul>
  );
};

export default ModelManager; 