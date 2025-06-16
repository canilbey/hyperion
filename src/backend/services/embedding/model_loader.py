from sentence_transformers import SentenceTransformer

def load_embedding_model(model_name):
    """
    Model adını alıp uygun SentenceTransformer modelini yükler.
    """
    return SentenceTransformer(model_name) 