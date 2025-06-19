import fitz  # PyMuPDF
import pdfplumber
import re
import nltk
import logging

def build_toc_hierarchy(toc):
    """
    toc: [ [level, title, page], ... ]
    Returns: [ {id, title, level, page, parent_id, ...}, ... ]
    """
    stack = []
    parents = []
    for idx, (level, title, page) in enumerate(toc):
        node = {
            "id": idx,
            "title": title,
            "level": level,
            "page": page,
            "parent_id": None,
            "content": "",
            "order": idx,
            "metadata": {"section_level": level, "page": page, "parent_title": title}
        }
        while stack and stack[-1]["level"] >= level:
            stack.pop()
        if stack:
            node["parent_id"] = stack[-1]["id"]
        stack.append(node)
        parents.append(node)
    return parents

def split_paragraphs_and_sentences(text, lang="turkish"):
    paragraphs = [p.strip() for p in text.split('\n') if p.strip()]
    sentences = []
    for para in paragraphs:
        try:
            sents = nltk.sent_tokenize(para, language=lang)
        except Exception:
            sents = [para]
        sentences.extend([s for s in sents if s.strip()])
    return sentences

def extract_headings_by_font_style(doc):
    parent_chunks = []
    child_chunks = []
    parent_id = 0
    current_parent_id = None
    font_sizes = []
    # Önce tüm font büyüklüklerini topla
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    font_sizes.append(span["size"])
    if not font_sizes:
        return parent_chunks, child_chunks
    unique_sizes = sorted(list(set(font_sizes)), reverse=True)
    heading_sizes = unique_sizes[:2]  # En büyük 2 font başlık için
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            block_text = ""
            block_is_heading = False
            block_font_size = None
            block_bold = False
            for line in block.get("lines", []):
                for span in line.get("spans", []):
                    block_text += span["text"]
                    if span["size"] in heading_sizes:
                        block_is_heading = True
                        block_font_size = span["size"]
                    if "Bold" in span["font"]:
                        block_bold = True
            text = block_text.strip()
            if not text:
                continue
            if block_is_heading or block_bold or is_title_like(text):
                parent_chunks.append({
                    "id": parent_id,
                    "title": text,
                    "content": "",
                    "order": parent_id,
                    "metadata": {"section_level": 1, "page": page_num+1, "parent_title": text, "font_size": block_font_size, "bold": block_bold}
                })
                current_parent_id = parent_id
                parent_id += 1
            else:
                if current_parent_id is None:
                    parent_chunks.append({
                        "id": parent_id,
                        "title": f"Page {page_num+1}",
                        "content": "",
                        "order": parent_id,
                        "metadata": {"section_level": 0, "page": page_num+1, "parent_title": f"Page {page_num+1}"}
                    })
                    current_parent_id = parent_id
                    parent_id += 1
                for sent in split_paragraphs_and_sentences(text):
                    child_chunks.append({
                        "parent_id": current_parent_id,
                        "content": sent,
                        "type": "Text",
                        "order": len([c for c in child_chunks if c["parent_id"] == current_parent_id]),
                        "metadata": {"page": page_num+1, "parent_title": parent_chunks[current_parent_id]["title"]}
                    })
    return parent_chunks, child_chunks

def fallback_page_parents(doc):
    parent_chunks = []
    child_chunks = []
    for page_num, page in enumerate(doc):
        parent_id = page_num
        parent_chunks.append({
            "id": parent_id,
            "title": f"Page {page_num+1}",
            "content": "",
            "order": parent_id,
            "metadata": {"section_level": 0, "page": page_num+1, "parent_title": f"Page {page_num+1}"}
        })
        blocks = page.get_text("blocks")
        for block in blocks:
            text = block[4].strip()
            if text:
                for sent in split_paragraphs_and_sentences(text):
                    child_chunks.append({
                        "parent_id": parent_id,
                        "content": sent,
                        "type": "Text",
                        "order": len([c for c in child_chunks if c["parent_id"] == parent_id]),
                        "metadata": {"page": page_num+1, "parent_title": f"Page {page_num+1}"}
                    })
    return parent_chunks, child_chunks

def extract_tables_and_images(file_path, parent_chunks):
    """
    pdfplumber ile tablo ve görselleri tespit et, bulundukları sayfanın en yakın parent_id'sine child olarak ata.
    """
    child_chunks = []
    with pdfplumber.open(file_path) as pdf:
        for page_num, page in enumerate(pdf.pages):
            # Tablo extraction
            tables = page.extract_tables()
            for t_idx, table in enumerate(tables):
                # Her hücreyi stringe çevir, None ise '' yap
                content = '\n'.join(['\t'.join([str(cell) if cell is not None else '' for cell in row]) for row in table if row])
                parent_id = find_parent_for_page(parent_chunks, page_num+1)
                child_chunks.append({
                    "parent_id": parent_id,
                    "type": "table",
                    "content": content,
                    "order": t_idx,
                    "metadata": {"page": page_num+1}
                })
            # Görsel extraction
            images = page.images
            for i_idx, img in enumerate(images):
                parent_id = find_parent_for_page(parent_chunks, page_num+1)
                bbox = img.get('bbox')
                if bbox is not None:
                    child_chunks.append({
                        "parent_id": parent_id,
                        "type": "image",
                        "content": f"Image on page {page_num+1}, bbox: {bbox}",
                        "order": i_idx,
                        "metadata": {"page": page_num+1, "bbox": bbox}
                    })
    return child_chunks

def find_parent_for_page(parent_chunks, page):
    # Sayfa numarasına göre en yakın parent_id'yi bul
    candidates = [p for p in parent_chunks if p.get("metadata", {}).get("page") == page]
    if candidates:
        return candidates[-1]["id"]
    # Hiçbiri yoksa ilk parent'a bağla
    return parent_chunks[0]["id"] if parent_chunks else None

def extract_lists(doc, parent_chunks):
    """
    PyMuPDF ile sayfa ve bloklarda madde işaretli veya numaralı listeleri tespit et, ilgili parent'a child olarak ata.
    """
    child_chunks = []
    bullet_patterns = [r'^\s*[\u2022\u2023\u25E6\u2043\u2219\*-]\s+', r'^\s*\d+\.|^\s*[a-zA-Z]\)']
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for block in blocks:
            block_text = " ".join([span["text"] for line in block.get("lines", []) for span in line.get("spans", [])]).strip()
            if not block_text:
                continue
            for pat in bullet_patterns:
                if re.match(pat, block_text):
                    parent_id = find_parent_for_page(parent_chunks, page_num+1)
                    child_chunks.append({
                        "parent_id": parent_id,
                        "type": "list",
                        "content": block_text,
                        "order": len([c for c in child_chunks if c.get("parent_id") == parent_id]),
                        "metadata": {"page": page_num+1}
                    })
                    break
    return child_chunks

def extract_pdf_document(file_path):
    logger = logging.getLogger(__name__)
    doc = fitz.open(file_path)
    toc = doc.get_toc()  # [ [level, title, page], ... ]
    parent_chunks = []
    child_chunks = []
    if toc:
        parent_chunks = build_toc_hierarchy(toc)
        for i, parent in enumerate(parent_chunks):
            start = parent["page"] - 1
            next_idx = i + 1
            while next_idx < len(parent_chunks) and parent_chunks[next_idx]["level"] > parent["level"]:
                next_idx += 1
            end = parent_chunks[next_idx]["page"] - 1 if next_idx < len(parent_chunks) else doc.page_count
            for page_num in range(start, end):
                page = doc[page_num]
                blocks = page.get_text("blocks")
                for block in blocks:
                    text = block[4].strip()
                    if text:
                        parent_id = parent["id"]
                        for sent in split_paragraphs_and_sentences(text):
                            child_chunks.append({
                                "parent_id": parent_id,
                                "content": sent,
                                "type": "Text",
                                "order": len([c for c in child_chunks if c["parent_id"] == parent_id]),
                                "metadata": {"page": page_num+1, "parent_title": parent["title"]}
                            })
    else:
        parent_chunks, child_chunks = extract_headings_by_font_style(doc)
    # Fallback: Eğer parent_chunks boşsa veya parent sayısı 1 ise (veya sadece default parent varsa), sayfa bazlı parent chunk oluştur
    if not parent_chunks or len(parent_chunks) == 1:
        parent_chunks, child_chunks = fallback_page_parents(doc)
    # Tablo ve görselleri child olarak ekle
    table_image_chunks = extract_tables_and_images(file_path, parent_chunks)
    child_chunks.extend(table_image_chunks)
    # Listeleri child olarak ekle
    list_chunks = extract_lists(doc, parent_chunks)
    child_chunks.extend(list_chunks)
    doc.close()
    # LOGGING: Parent ve child chunk sayısı ve örnekler
    logger.info(f"[PDF PARSE] Parent chunk sayısı: {len(parent_chunks)}")
    logger.info(f"[PDF PARSE] Child chunk sayısı: {len(child_chunks)}")
    for i, parent in enumerate(parent_chunks[:3]):
        logger.info(f"[PDF PARSE] Parent {i}: title='{parent.get('title')}', content='{parent.get('content','')[:80]}...'")
    for i, child in enumerate(child_chunks[:3]):
        logger.info(f"[PDF PARSE] Child {i}: parent_id={child.get('parent_id')}, type={child.get('type')}, content='{child.get('content','')[:80]}...'")
    return parent_chunks, child_chunks

def is_title_like(text):
    if not text or len(text) > 120:
        return False
    if re.match(r'^(\d+\.)+(\d+)?', text.strip()):
        return True
    if text.isupper() and len(text) < 40:
        return True
    if re.match(r'^(Bölüm|Section|Başlık)', text.strip(), re.IGNORECASE):
        return True
    return False 