import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ChatList from "./components/ChatList";
import ModelManager from "./components/ModelManager";
import FileManager from "./components/FileManager";
import { getModels } from "./services/modelService";
import { getFiles } from "./services/fileService";
import { getChats, deleteChat } from "./services/chatService";
import ChatContainer from "./components/ChatContainer";

const PROFILE_MENU = [
  { key: "profile", label: "Profile" },
  { key: "settings", label: "Settings" },
];

function ProfileDropdown({ open, onSelect }) {
  if (!open) return null;
  return (
    <div className="absolute right-0 mt-2 w-44 bg-blue-grey-4 text-text rounded-xl shadow-2xl border border-blue-grey-3 z-50">
      {PROFILE_MENU.map(item => (
        <button
          key={item.key}
          className="w-full text-left px-5 py-3 rounded-xl transition font-medium bg-blue-grey-4 text-blue-grey-2 hover:bg-blue-grey-3 hover:text-white focus:outline-none focus:ring-2 focus:ring-accent"
          onClick={() => onSelect(item.key)}
        >
          {item.label}
        </button>
      ))}
    </div>
  );
}

function MainContent({ page, selectedChatId, setSelectedChatId, models, selectedModel, setSelectedModel, chats, setChats }) {
  // Chat alanı (ChatGPT tarzı)
  if (page === "chats") {
    return <ChatContainer
      selectedChatId={selectedChatId}
      setSelectedChatId={setSelectedChatId}
      models={models}
      selectedModel={selectedModel}
      setSelectedModel={setSelectedModel}
      chats={chats}
      setChats={setChats}
    />;
  }

  // Model alanı
  if (page === "models") {
    return <ModelManager />;
  }

  // File alanı
  if (page === "files") {
    return <FileManager />;
  }

  // Default
  return <div className="p-8 text-xl">Ana Sayfa</div>;
}

export default function App() {
  const [selectedNav, setSelectedNav] = useState("chats");
  const [mainPage, setMainPage] = useState("chats");
  const [profileOpen, setProfileOpen] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [models, setModels] = useState([]);
  const [files, setFiles] = useState([]);
  const [modelError, setModelError] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [chats, setChats] = useState([]);
  const [selectedChatId, setSelectedChatId] = useState(null);
  const [openModelId, setOpenModelId] = useState(null);
  const [selectedModel, setSelectedModel] = useState("");

  useEffect(() => {
    getModels().then(setModels).catch(() => setModelError("Modeller alınamadı"));
    getFiles().then(setFiles).catch(() => setFileError("Dosyalar alınamadı"));
    getChats().then(setChats).catch(() => setChats([]));
  }, []);

  const handleDeleteChat = async (chatId) => {
    if (!window.confirm("Bu sohbeti silmek istediğinizden emin misiniz?")) return;
    try {
      await deleteChat(chatId);
      setChats(chats.filter(c => c.chat_id !== chatId));
      if (selectedChatId === chatId) {
        setSelectedChatId(null);
      }
    } catch (err) {
      console.error("Sohbet silinemedi:", err);
    }
  };

  // Sidebar alt içerik
  let contentList = null;
  if (selectedNav === "chats") {
    contentList = (
      <>
        <div className="mb-2 font-bold text-md flex items-center justify-between">
          <span>Chats</span>
          <button
            className="w-8 h-8 flex items-center justify-center rounded bg-blue-grey-5 text-white hover:bg-blue-grey-4 transition text-xl p-0"
            onClick={() => setSelectedChatId(null)}
            aria-label="Yeni Chat"
          >
            <span className="material-icons text-lg">add</span>
          </button>
        </div>
        <ul className="flex flex-col gap-1 mb-4">
          {chats.length === 0 && <li className="text-blue-grey-2">Hiç sohbet yok</li>}
          {chats.map(chat => (
            <li key={chat.chat_id} className="relative group">
              <div className="flex items-center">
                <button
                  className={`flex-1 text-left px-3 py-2 rounded transition font-medium ${selectedChatId === chat.chat_id ? 'bg-blue-grey-3 text-white' : 'bg-blue-grey-5 text-white hover:bg-blue-grey-4'}`}
                  onClick={() => setSelectedChatId(chat.chat_id)}
                >
                  {chat.label || chat.chat_id}
                </button>
                <button
                  className="w-8 h-8 flex items-center justify-center rounded bg-red-600 text-white hover:bg-red-700 transition text-sm ml-2 opacity-0 group-hover:opacity-100"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteChat(chat.chat_id);
                  }}
                  aria-label="Sohbeti Sil"
                  title="Sohbeti Sil"
                >
                  🗑️
                </button>
              </div>
            </li>
          ))}
        </ul>
      </>
    );
  }
  if (selectedNav === "models") {
    contentList = (
      <>
        <div className="mb-2 flex items-center justify-between">
          <span className="font-bold text-md">Modeller</span>
          <button
            className="w-8 h-8 flex items-center justify-center rounded bg-blue-grey-5 text-white hover:bg-blue-grey-4 transition text-xl p-0"
            onClick={() => setOpenModelId("__new__")}
            aria-label="Model Ekle"
          >
            <span className="material-icons text-lg">add</span>
          </button>
        </div>
        {modelError && <div className="text-red-500">{modelError}</div>}
        <ul className="flex flex-col gap-1 mb-4">
          {models.map(model => (
            <li key={model.model_id}>
              <button
                className={`w-full text-left px-3 py-2 rounded transition font-medium ${openModelId === model.model_id ? 'bg-blue-grey-3 text-white' : 'bg-blue-grey-5 text-white hover:bg-blue-grey-4'}`}
                onClick={() => { setMainPage("models"); setOpenModelId(model.model_id); }}
              >
                {model.model_name}
              </button>
            </li>
          ))}
        </ul>
      </>
    );
    contentList = (
      <>
        {contentList}
      </>
    );
  }
  if (selectedNav === "files") {
    contentList = (
      <div className="mb-2 flex items-center justify-between">
        <span className="font-bold text-md">Dosyalar</span>
        <button
          className="w-8 h-8 flex items-center justify-center rounded bg-blue-grey-5 text-white hover:bg-blue-grey-4 transition text-xl p-0"
          onClick={() => {/* dosya ekleme işlemi */}}
          aria-label="Dosya Ekle"
        >
          <span className="material-icons text-lg">add</span>
        </button>
      </div>
    );
    contentList = (
      <>
        {contentList}
        {fileError && <div className="text-red-500">{fileError}</div>}
        <FileManager />
      </>
    );
  }

  return (
    <div className="flex h-screen bg-background text-text font-sans">
      {/* Sidebar toggle butonu */}
      <button
        className="absolute top-4 left-4 z-50 w-10 h-10 rounded-full bg-blue-grey-3 text-white flex items-center justify-center shadow-lg hover:bg-blue-grey-2 transition md:hidden"
        onClick={() => setSidebarOpen(v => !v)}
        aria-label="Menüyü Aç/Kapat"
      >
        <span className="material-icons">{sidebarOpen ? "chevron_left" : "menu"}</span>
      </button>
      <Sidebar
        selectedNav={selectedNav}
        setSelectedNav={nav => { setSelectedNav(nav); setMainPage(nav); }}
        contentList={<>{contentList}</>}
        onLogoClick={() => { setSelectedNav("chats"); setMainPage("chats"); setSelectedChatId(null); }}
        open={sidebarOpen}
      />
      <main className="flex-1 flex flex-col relative">
        {/* Sağ üst profil butonu */}
        <div className="flex justify-end items-center p-4 pb-0">
          <div className="relative">
            <button
              className="w-10 h-10 rounded-full bg-blue-grey-3 text-white flex items-center justify-center text-lg font-bold shadow hover:bg-blue-grey-2 focus:outline-none focus:ring-2 focus:ring-accent transition"
              onClick={() => setProfileOpen(v => !v)}
            >
              <span className="material-icons">person</span>
            </button>
            <ProfileDropdown open={profileOpen} onSelect={key => { setMainPage(key); setProfileOpen(false); }} />
          </div>
        </div>
        {/* Ana içerik alanı */}
        <div className="flex-1 overflow-auto">
          <MainContent
            page={mainPage}
            selectedChatId={selectedChatId}
            setSelectedChatId={setSelectedChatId}
            models={models}
            selectedModel={selectedModel}
            setSelectedModel={setSelectedModel}
            chats={chats}
            setChats={setChats}
          />
        </div>
      </main>
    </div>
  );
} 