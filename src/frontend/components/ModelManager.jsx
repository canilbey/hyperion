import React, { useState, useRef, useEffect } from "react";
import { getModels, addModel, deleteModel, updateModel } from "../services/modelService";

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

function ModelForm({ onSave, onCancel, initialData }) {
  const PROVIDERS = [
    { value: "openrouter", label: "OpenRouter" },
    { value: "openai", label: "OpenAI" },
    { value: "anthropic", label: "Anthropic" },
    { value: "local", label: "Local" }
  ];
  const [form, setForm] = useState({
    model_id: initialData?.model_id || "",
    provider: initialData?.provider || "openrouter",
    model: initialData?.model || "",
    model_name: initialData?.model_name || "",
    api_key: initialData?.api_key || "",
    system_prompt: initialData?.system_prompt || "",
    temperature: initialData?.temperature ?? 0.7,
    max_tokens: initialData?.max_tokens ?? 4000,
    token_limit: initialData?.token_limit ?? "",
    is_active: initialData?.is_active ?? true,
    knowledge_table_name: initialData?.knowledge_table_name || "",
    knowledge_table_id: initialData?.knowledge_table_id || ""
  });
  const [error, setError] = useState(null);
  const handleChange = e => {
    const { name, value, type, checked } = e.target;
    setForm(f => ({ ...f, [name]: type === "checkbox" ? checked : value }));
  };
  const handleSubmit = async e => {
    e.preventDefault();
    if (!form.provider || !form.model || !form.model_name || !form.api_key || !form.system_prompt) {
      setError("Tüm zorunlu alanları doldurun.");
      return;
    }
    try {
      await onSave(form);
    } catch (err) {
      setError(err.message || "Model eklenemedi");
    }
  };
  return (
    <form className="bg-blue-grey-5 p-8 rounded-xl shadow-xl w-full max-w-4xl mx-auto" onSubmit={handleSubmit}>
      <div className="text-lg font-bold mb-6">Model Konfigürasyonu</div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Sol: Opsiyonel Alanlar */}
        <div className="flex flex-col gap-4">
          <div>
            <label className="block mb-1">Temperature</label>
            <input name="temperature" type="number" step="0.01" min="0" max="2" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.temperature} onChange={handleChange} />
          </div>
          <div>
            <label className="block mb-1">Max Tokens</label>
            <input name="max_tokens" type="number" min="1" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.max_tokens} onChange={handleChange} />
          </div>
          <div>
            <label className="block mb-1">Token Limit</label>
            <input name="token_limit" type="number" min="1" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.token_limit} onChange={handleChange} />
          </div>
          <div>
            <label className="block mb-1">Aktif mi?</label>
            <input name="is_active" type="checkbox" checked={form.is_active} onChange={handleChange} />
          </div>
          <div>
            <label className="block mb-1">Knowledge Table Name</label>
            <input name="knowledge_table_name" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.knowledge_table_name} onChange={handleChange} />
          </div>
          <div>
            <label className="block mb-1">Knowledge Table ID</label>
            <input name="knowledge_table_id" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.knowledge_table_id} onChange={handleChange} />
          </div>
        </div>
        {/* Sağ: Zorunlu Alanlar */}
        <div className="flex flex-col gap-4">
          <input type="hidden" name="model_id" value={form.model_id} />
          <div>
            <label className="block mb-1">Provider <span className="text-red-400">*</span></label>
            <select name="provider" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.provider} onChange={handleChange} required>
              {PROVIDERS.map(p => <option key={p.value} value={p.value}>{p.label}</option>)}
            </select>
          </div>
          <div>
            <label className="block mb-1">Model <span className="text-red-400">*</span></label>
            <input name="model" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.model} onChange={handleChange} required />
          </div>
          <div>
            <label className="block mb-1">Model Adı <span className="text-red-400">*</span></label>
            <input name="model_name" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.model_name} onChange={handleChange} required />
          </div>
          <div>
            <label className="block mb-1">API Key <span className="text-red-400">*</span></label>
            <input name="api_key" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.api_key} onChange={handleChange} required />
          </div>
          <div>
            <label className="block mb-1">System Prompt <span className="text-red-400">*</span></label>
            <textarea name="system_prompt" className="w-full bg-blue-grey-4 rounded px-4 py-2 text-white" value={form.system_prompt} onChange={handleChange} required />
          </div>
        </div>
      </div>
      {error && <div className="text-red-500 text-sm mt-4">{error}</div>}
      <div className="flex gap-3 mt-8 justify-start">
        <button type="submit" className="bg-blue-grey-3 text-white px-6 py-2 rounded-xl hover:bg-blue-grey-2 transition font-bold">Kaydet</button>
        <button type="button" className="bg-blue-grey-4 text-white px-6 py-2 rounded-xl hover:bg-blue-grey-3 transition" onClick={onCancel}>Kapat</button>
      </div>
    </form>
  );
}

const ModelManager = ({ openModelId: externalOpenModelId, onOpenModel }) => {
  const [models, setModels] = useState([]);
  const [openModelId, setOpenModelId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const modelRefs = useRef({});

  useEffect(() => {
    fetchModels();
  }, []);

  useEffect(() => {
    // Sidebar'dan model seçilirse aç ve odaklan
    if (externalOpenModelId) {
      setOpenModelId(externalOpenModelId);
      setTimeout(() => {
        if (modelRefs.current[externalOpenModelId]) {
          modelRefs.current[externalOpenModelId].scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 100);
    }
  }, [externalOpenModelId]);

  const fetchModels = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getModels();
      setModels(data);
    } catch (err) {
      setError(err.message || "Modeller alınamadı");
    } finally {
      setLoading(false);
    }
  };

  const handleAccordionClick = (modelId) => {
    if (openModelId === modelId) {
      setOpenModelId(null);
      if (onOpenModel) onOpenModel(null);
    } else {
      setOpenModelId(modelId);
      if (onOpenModel) onOpenModel(modelId);
    }
  };

  const handleSave = async (form) => {
    await addModel({
      provider: form.provider,
      model: form.model,
      model_name: form.model_name,
      api_key: form.api_key,
      system_prompt: form.system_prompt,
      temperature: parseFloat(form.temperature),
      max_tokens: form.max_tokens ? parseInt(form.max_tokens) : 4000,
      token_limit: form.token_limit ? parseInt(form.token_limit) : null,
      is_active: !!form.is_active,
      knowledge_table_name: form.knowledge_table_name || null,
      knowledge_table_id: form.knowledge_table_id || null
    });
    setOpenModelId(null);
    fetchModels();
  };
  const handleUpdate = async (form) => {
    const updateFields = {
      model_name: form.model_name,
      model: form.model,
      system_prompt: form.system_prompt,
      api_key: form.api_key,
      temperature: parseFloat(form.temperature),
      max_tokens: form.max_tokens ? parseInt(form.max_tokens) : 4000,
      token_limit: form.token_limit ? parseInt(form.token_limit) : null,
      is_active: !!form.is_active,
      knowledge_table_name: form.knowledge_table_name || null,
      knowledge_table_id: form.knowledge_table_id || null
    };
    await updateModel(form.model_id, updateFields);
    setOpenModelId(null);
    fetchModels();
  };
  const handleDelete = async (id) => {
    if (!window.confirm("Model silinsin mi?")) return;
    try {
      await deleteModel(id);
      fetchModels();
    } catch (err) {
      setError(err.message || "Model silinemedi");
    }
  };

  return (
    <div className="flex flex-col gap-2">
      <button className="bg-blue-500 text-white px-3 py-1 rounded mb-2 w-max" onClick={() => setOpenModelId("__new__")}>Model Ekle</button>
      {loading && <div>Yükleniyor...</div>}
      {error && <div className="text-red-500">{error}</div>}
      <ul className="flex flex-col gap-2">
        {models.map((model) => (
          <li key={model.model_id} ref={el => modelRefs.current[model.model_id] = el}>
            <div
              className={`flex items-center justify-between px-5 py-4 rounded-2xl cursor-pointer transition bg-blue-grey-5 hover:bg-blue-grey-4 text-white ${openModelId === model.model_id ? 'ring-2 ring-blue-grey-3' : ''}`}
              onClick={() => handleAccordionClick(model.model_id)}
            >
              <span>{model.model_name}</span>
              <span className="flex gap-2">
                <button
                  className="material-icons text-red-300 hover:text-red-500 text-2xl bg-transparent border-none p-0"
                  onClick={e => { e.stopPropagation(); handleDelete(model.model_id); }}
                  aria-label="Sil"
                >
                  delete
                </button>
              </span>
            </div>
            {openModelId === model.model_id && (
              <div className="bg-blue-grey-4 rounded-b-2xl p-6 mt-1">
                <ModelForm
                  onSave={handleUpdate}
                  onCancel={() => setOpenModelId(null)}
                  initialData={model}
                />
              </div>
            )}
          </li>
        ))}
        {openModelId === "__new__" && (
          <li className="bg-blue-grey-4 rounded-2xl p-6 mt-1">
            <ModelForm onSave={handleSave} onCancel={() => setOpenModelId(null)} />
          </li>
        )}
      </ul>
    </div>
  );
};

export default ModelManager; 