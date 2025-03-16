from setuptools import setup, find_packages

setup(
    name="backend",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'fastapi>=0.99.0',
        'uvicorn>=0.15.0',
        'pytest>=8.0.0',
        'pymupdf>=1.26.3',  # Patched CVE-2024-27308
        'opentelemetry-sdk>=1.31.0',
        'opentelemetry-exporter-prometheus>=0.52.0',
        'opentelemetry-instrumentation-fastapi>=0.47.0',
        'httpx>=0.27.0',
        'prometheus-client>=0.20.0',
        'pymilvus>=2.3.3',
        'langchain>=0.2.0',
        'python-dotenv>=1.0.0'
    ],
)