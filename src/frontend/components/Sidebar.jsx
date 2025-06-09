import React from "react";

const NAV_ITEMS = [
  { key: "chats", label: "Chats", icon: "chat_bubble" },
  { key: "models", label: "Model Management", icon: "psychology" },
  { key: "files", label: "File Management", icon: "folder" },
];

const Sidebar = ({ selectedNav, setSelectedNav, contentList, onLogoClick, open }) => (
  <aside className={`flex flex-col h-full ${open ? 'w-64' : 'w-20'} bg-blue-grey-5 text-white shadow-2xl shadow-blue-grey-4/80 rounded-r-lg p-0 transition-all duration-300 z-40`}>
    {/* Üst: Logo ve Navigation */}
    <div className={`flex flex-col gap-8 p-6 pb-2 ${open ? '' : 'items-center p-2'}`}>
      <div className="flex items-center gap-2 cursor-pointer select-none" onClick={onLogoClick}>
        <div className="w-8 h-8 bg-blue-grey-3 rounded-full flex items-center justify-center text-xl font-bold">L</div>
        {open && <span className="text-lg font-bold tracking-wide">Hyperion</span>}
      </div>
      <nav className={`flex flex-col gap-3 mt-4 ${open ? '' : 'items-center'}`}>
        {NAV_ITEMS.map((item) => (
          <button
            key={item.key}
            className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition shadow-none border-none outline-none
              ${selectedNav === item.key
                ? 'bg-blue-grey-3 text-white'
                : 'bg-blue-grey-5 text-white hover:bg-blue-grey-4'}
              ${!open ? 'justify-center px-0' : ''}
            `}
            onClick={() => setSelectedNav(item.key)}
          >
            <span className="material-icons text-2xl align-middle">{item.icon}</span>
            {open && <span className="align-middle">{item.label}</span>}
          </button>
        ))}
      </nav>
    </div>
    {/* Divider */}
    <div className={`w-full h-px bg-blue-grey-4/60 my-2 ${open ? '' : 'hidden'}`}></div>
    {/* Alt: İçerik Listesi */}
    <div className={`flex-1 overflow-y-auto p-4 pt-0 transition-all duration-300 ${open ? '' : 'p-2'}`}>
      {open ? contentList : null}
    </div>
  </aside>
);

export default Sidebar; 