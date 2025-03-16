from hyperion_sdk import RagClient

client = RagClient(
    api_key="your_api_key",
    base_url="https://api.hyperion.ai/v1"
)

# Upload document
upload_response = client.upload_file("document.pdf")
print(f"Uploaded file ID: {upload_response.file_id}")

# Query RAG system
query_result = client.query(
    "What is Retrieval-Augmented Generation?",
    model_config="default"
)
print(f"Answer: {query_result.answer}")