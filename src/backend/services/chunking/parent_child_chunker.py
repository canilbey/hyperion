import re

def is_section_title_element(el):
    # Unstructured elementlerinde category/type alanı varsa başlık olarak kabul et
    for attr in [getattr(el, 'category', None), getattr(el, 'type', None)]:
        if attr and str(attr).lower() in ["title", "sectionheader", "heading"]:
            return True
    return False

def is_section_title_text(text):
    if not text or not isinstance(text, str):
        return False
    text_stripped = text.strip()
    # Numara ile başlayan başlık (örn. 2., 4.1.7)
    if re.match(r'^(\d+\.)+(\d+)?\s', text_stripped):
        return True
    # İki nokta üst üste ile biten başlık
    if text_stripped.endswith(":"):
        return True
    # Kısa ve ilk harfi büyük (örn. "Giriş", "Sonuç")
    if len(text_stripped) < 40 and text_stripped.istitle():
        return True
    return False

def chunk_elements(elements):
    """
    Unstructured element listesini parent-child chunk yapısına dönüştürür.
    Başlıklar parent, diğer elementler child olarak işlenir.
    Başlık tespiti için önce elementin category/type alanı, yoksa regex ile text kontrolü yapılır.
    Dile bağımlı hardcoded anahtar kelime kullanılmaz.
    Unstructured elementlerinde parent_title metadata'sı varsa parent ve child chunk'a eklenir.
    Orijinal elementin tüm metadata'sı child chunk'a aktarılır.
    """
    parent_chunks = []
    child_chunks = []
    current_parent = None
    current_parent_id = 0
    section_level = 1
    section_type = "section"
    current_parent_title = None

    if not elements:
        current_parent = {
            "id": 0,
            "title": "Document Content",
            "content": "",
            "order": 0,
            "metadata": {"section_level": 0, "section_type": "document"}
        }
        parent_chunks.append(current_parent)
        child_chunks.append({
            "parent_id": 0,
            "content": "[No readable content found in document]",
            "type": "Text",
            "order": 0,
            "metadata": {"section_level": 0, "section_type": "document"}
        })
        return parent_chunks, child_chunks

    for el in elements:
        text = getattr(el, 'text', None)
        parent_title = getattr(getattr(el, 'metadata', None), 'parent_title', None)
        if is_section_title_element(el) or is_section_title_text(text):
            current_parent_title = parent_title if parent_title else (text.strip() if text else f"Section {current_parent_id}")
            current_parent = {
                "id": current_parent_id,
                "title": current_parent_title,
                "content": "",
                "order": current_parent_id,
                "metadata": {"section_level": section_level, "section_type": section_type, "parent_title": current_parent_title}
            }
            parent_chunks.append(current_parent)
            current_parent_id += 1
        else:
            if current_parent is None:
                current_parent_title = parent_title if parent_title else "Document Content"
                current_parent = {
                    "id": current_parent_id,
                    "title": current_parent_title,
                    "content": "",
                    "order": current_parent_id,
                    "metadata": {"section_level": 0, "section_type": "document", "parent_title": current_parent_title}
                }
                parent_chunks.append(current_parent)
                current_parent_id += 1
            text_content = text
            if text_content and text_content.strip():
                # Orijinal elementin tüm metadata'sını child chunk'a ekle
                orig_metadata = getattr(el, 'metadata', None)
                child_metadata = current_parent["metadata"].copy()
                if orig_metadata:
                    # dict'e dönüştürülüp birleştirilebilir
                    try:
                        orig_dict = orig_metadata.to_dict() if hasattr(orig_metadata, 'to_dict') else dict(orig_metadata)
                        child_metadata.update(orig_dict)
                    except Exception:
                        pass
                child_chunks.append({
                    "parent_id": current_parent["id"],
                    "content": text_content,
                    "type": getattr(el, 'category', getattr(el, 'type', 'Text')),
                    "order": len([c for c in child_chunks if c["parent_id"] == current_parent["id"]]),
                    "metadata": child_metadata
                })

    if not child_chunks and parent_chunks:
        child_chunks.append({
            "parent_id": parent_chunks[0]["id"],
            "content": "[No readable content found in document]",
            "type": "Text",
            "order": 0,
            "metadata": parent_chunks[0]["metadata"].copy()
        })
    elif not parent_chunks and child_chunks:
        parent_chunks.append({
            "id": 0,
            "title": "Document Content",
            "content": "",
            "order": 0,
            "metadata": {"section_level": 0, "section_type": "document"}
        })
        for c in child_chunks:
            c["parent_id"] = 0
            c["metadata"] = {"section_level": 0, "section_type": "document"}

    return parent_chunks, child_chunks 