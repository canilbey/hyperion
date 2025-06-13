import React, { useState, useEffect } from "react";
import Sidebar from "./components/Sidebar";
import ChatList from "./components/ChatList";
import ModelManager from "./components/ModelManager";
import FileManager from "./components/FileManager";
import { getModels } from "./services/modelService";
import { getFiles } from "./services/fileService";

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

function MainContent({ page, chats, models, files, onModelUpdate, onModelDelete, onFileDelete }) {
  const [selectedModel, setSelectedModel] = useState(null);
  const [selectedFile, setSelectedFile] = useState(null);
  const [modelEdit, setModelEdit] = useState(null);

  // Chat alanı (ChatGPT tarzı)
  if (page === "chats") {
    return (
      <div className="flex flex-col h-full max-w-3xl mx-auto py-8">
        <div className="flex-1 overflow-y-auto space-y-6 pb-8">
          {/* Örnek mesajlar */}
          <div className="flex justify-end">
            <div className="bg-blue-grey-3 text-white rounded-2xl px-5 py-3 max-w-lg shadow">Merhaba, boğaz şişkinliğine ne iyi gelir?</div>
          </div>
          <div className="flex justify-start">
            <div className="bg-blue-grey-4 text-white rounded-2xl px-5 py-3 max-w-lg shadow">
              Boğaz şişkinliği genellikle enfeksiyon, tahriş veya alerji gibi nedenlerden kaynaklanır...<br/>
              <ul className="list-disc pl-6 mt-2">
                <li><b>Evde Uygulanabilecek Destekleyici Yöntemler</b></li>
                <li>Tuzlu su gargarası</li>
                <li>Ilık sıvılar tüketmek</li>
              </ul>
            </div>
          </div>
        </div>
        <form className="flex gap-3 mt-auto bg-blue-grey-5 rounded-2xl p-4 shadow-xl">
          <input
            className="flex-1 bg-blue-grey-4 text-white rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-blue-grey-3"
            type="text"
            placeholder="Herhangi bir şey sor..."
          />
          <button type="submit" className="bg-blue-grey-3 text-white px-6 py-3 rounded-xl hover:bg-blue-grey-2 transition font-bold">Gönder</button>
        </form>
      </div>
    );
  }

  // Model alanı
  if (page === "models") {
    return <ModelManager />;
  }

  // File alanı
  if (page === "files") {
    return (
      <div className="flex gap-8 p-8">
        <ul className="flex flex-col gap-3 w-80">
          {files.map(file => (
            <li key={file.id}>
              <div className={`flex items-center justify-between px-5 py-4 rounded-2xl cursor-pointer transition bg-blue-grey-5 hover:bg-blue-grey-4 text-white ${selectedFile && selectedFile.id === file.id ? 'ring-2 ring-blue-grey-3' : ''}`}
                onClick={() => setSelectedFile(file)}>
                <span>{file.name}</span>
                <button
                  className="material-icons text-red-300 hover:text-red-500 text-2xl bg-transparent border-none p-0 ml-2"
                  onClick={e => { e.stopPropagation(); onFileDelete && onFileDelete(file.id); }}
                  aria-label="Sil"
                >
                  delete
                </button>
              </div>
            </li>
          ))}
        </ul>
        {/* Detay paneli */}
        {selectedFile && (
          <div className="flex-1 max-w-lg bg-blue-grey-5 rounded-2xl p-8 shadow-xl text-white">
            <div className="mb-4 text-lg font-bold">Dosya Metadata</div>
            <div className="space-y-4">
              <div><b>Dosya Adı:</b> {selectedFile.name}</div>
              <div><b>Yüklenme Tarihi:</b> 2024-06-09</div>
              <div><b>Dosya Boyutu:</b> 1.2 MB</div>
              <div><b>Chunk Sayısı:</b> 12</div>
              <div><b>Chunking Metodu:</b> Otomatik</div>
              <div className="flex gap-3 mt-4">
                <button className="bg-blue-grey-4 text-white px-6 py-2 rounded-xl hover:bg-blue-grey-3 transition" onClick={() => setSelectedFile(null)}>Kapat</button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
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
  const [openModelId, setOpenModelId] = useState(null);

  useEffect(() => {
    getModels().then(setModels).catch(() => setModelError("Modeller alınamadı"));
    getFiles().then(setFiles).catch(() => setFileError("Dosyalar alınamadı"));
  }, []);

  // Sidebar alt içerik
  let contentList = null;
  if (selectedNav === "chats") {
    contentList = (
      <div className="mb-2 flex items-center justify-between">
        <span className="font-bold text-md">Chatler</span>
        <button
          className="w-8 h-8 flex items-center justify-center rounded bg-blue-grey-5 text-white hover:bg-blue-grey-4 transition text-xl p-0"
          onClick={() => {/* yeni chat açma işlemi */}}
          aria-label="Yeni Chat"
        >
          <span className="material-icons text-lg">add</span>
        </button>
      </div>
    );
    contentList = (
      <>
        {contentList}
        <ChatList chats={chats} selectedChatId={1} onSelect={()=>setMainPage("chats")} />
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
        <FileManager files={files} selectedId={null} onSelect={()=>{}} onAdd={()=>{}} onDelete={()=>{}} onEdit={()=>{}} />
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
        contentList={<>
          {contentList}
        </>}
        onLogoClick={() => { setSelectedNav("chats"); setMainPage("chats"); }}
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
          {selectedNav === "models" ? (
            <ModelManager openModelId={openModelId} onOpenModel={setOpenModelId} />
          ) : (
            <MainContent page={mainPage} chats={chats} models={models} files={files} />
          )}
        </div>
      </main>
    </div>
  );
} 