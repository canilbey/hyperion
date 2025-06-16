import logging
import json

def safe_serialize(obj):
    """
    Objede binary karakter varsa temizle ve JSON serializable hale getir.
    """
    if isinstance(obj, str):
        # String'deki problematik karakterleri temizle
        return ''.join(char for char in obj if ord(char) < 127 or char.isalnum() or char.isspace())
    elif isinstance(obj, list):
        return [safe_serialize(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: safe_serialize(value) for key, value in obj.items()}
    else:
        return obj

def log_search(query, results, metadata):
    """
    Arama ve retrieval işlemlerini detaylı olarak logla.
    Encoding sorunlarını önler.
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Tüm data'yı encoding-safe hale getir
        safe_query = safe_serialize(query)
        safe_results = safe_serialize(results)
        safe_metadata = safe_serialize(metadata)
        
        log_entry = {
            "query": safe_query,
            "results": safe_results,
            "metadata": safe_metadata
        }
        
        # JSON serialization test
        json.dumps(log_entry, ensure_ascii=True)
        
        logger.info(f"Search logged: query={safe_query[:100]}, results_count={len(safe_results) if isinstance(safe_results, list) else 0}")
        return log_entry
        
    except Exception as e:
        logger.error(f"Failed to log search: {str(e)}")
        # Minimal fallback log
        return {
            "query": "[ENCODING_ERROR]",
            "results": [],
            "metadata": {"error": str(e)}
        } 