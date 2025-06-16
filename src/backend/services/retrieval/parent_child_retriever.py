def retrieve_context(child_chunk_id, db):
    """
    Child chunk'ın parent'ını bul ve bağlam olarak döndür.
    """
    # Örnek: SELECT * FROM parent_chunks WHERE id = (SELECT parent_id FROM child_chunks WHERE id=...)
    parent_chunk = db.get_parent_by_child(child_chunk_id)
    return parent_chunk 