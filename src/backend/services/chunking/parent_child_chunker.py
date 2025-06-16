def chunk_elements(elements):
    """
    unstructured element listesini parent-child chunk yapısına dönüştürür.
    Başlıklar parent, diğer elementler child olarak işlenir.
    Boş element listesi durumunda da çalışır.
    """
    parent_chunks = []
    child_chunks = []
    current_parent = None
    current_parent_id = 0
    
    # Boş element listesi durumu
    if not elements:
        # En azından bir dummy parent ve child oluştur
        current_parent = {
            "id": 0,
            "title": "Document Content",
            "content": "",
            "order": 0
        }
        parent_chunks.append(current_parent)
        
        child_chunks.append({
            "parent_id": 0,
            "content": "[No readable content found in document]",
            "type": "Text",
            "order": 0
        })
        
        return parent_chunks, child_chunks
    
    for el in elements:
        if hasattr(el, 'category') and el.category == "Title":
            current_parent = {
                "id": current_parent_id,
                "title": getattr(el, 'text', None),
                "content": "",
                "order": current_parent_id
            }
            parent_chunks.append(current_parent)
            current_parent_id += 1
        else:
            if current_parent is None:
                # Başlıksız child'lar için dummy parent
                current_parent = {
                    "id": current_parent_id,
                    "title": "Document Content",
                    "content": "",
                    "order": current_parent_id
                }
                parent_chunks.append(current_parent)
                current_parent_id += 1
            
            text_content = getattr(el, 'text', None)
            if text_content and text_content.strip():  # Sadece boş olmayan içerik ekle
                child_chunks.append({
                    "parent_id": current_parent["id"],
                    "content": text_content,
                    "type": getattr(el, 'category', 'Text'),
                    "order": len([c for c in child_chunks if c["parent_id"] == current_parent["id"]])
                })
    
    # Hiç child chunk yoksa dummy ekle
    if not child_chunks and parent_chunks:
        child_chunks.append({
            "parent_id": parent_chunks[0]["id"],
            "content": "[No readable content found in document]",
            "type": "Text",
            "order": 0
        })
    
    return parent_chunks, child_chunks 